# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json

from typing import List
from botbuilder.core import CardFactory, TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount, TaskModuleRequest, TaskModuleResponse, TaskModuleTaskInfo, TaskModuleContinueResponse, TaskModuleMessageResponse
from botbuilder.schema._connector_client_enums import ActionTypes
from langchain_core.messages.tool import ToolMessage
from mcp_client import create_agent, get_tool_details

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"

class TeamsMcpClientAgent(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str, mcp_servers_list_path) -> None:
        self._app_id = app_id
        self._app_password = app_password
        self._agent = None
        self._agent_cm = None
        self._selected_tools = []
        self._mcp_servers_list_path = mcp_servers_list_path
        
    async def initialize_agent(self, turn_context: TurnContext = None):
        """Initialize the agent if it hasn't been initialized yet"""
        if self._agent is None:
            # If turn_context is provided, show the select tools card
            if turn_context:
                await self._send_select_tools_card(turn_context)
            else:
                # Initialize with all tools if no context is available
                self._agent_cm = create_agent()
                self._agent = await self._agent_cm.__aenter__()
                print("Agent initialized with all MCP tools")
                
    async def _send_select_tools_card(self, turn_context: TurnContext):
        """Send a card with a button to select tools"""
        card = HeroCard(
            title="Agent Initialization",
            text="The agent needs to be initialized with tools. Would you like to select specific tools?",
            buttons=[
                CardAction(
                    type="invoke",
                    title="Select Tools",
                    value={"type": "task/fetch", "data": "SELECT_TOOLS"}
                )
            ]
        )
        await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))
        
    async def _get_available_tools(self):
        """Get list of available tools from MCP servers list"""
        try:
            tools_by_server, all_tools = await get_tool_details(self._mcp_servers_list_path)
            return tools_by_server, all_tools
        except Exception as e:
            print(f"Error getting available tools: {e}")
            return []

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: [TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome to the team { member.given_name } { member.surname }. "
                )
                
    async def on_teams_task_module_fetch(
        self, turn_context: TurnContext, task_module_request: TaskModuleRequest
    ) -> TaskModuleResponse:
        """Handles the Teams task module fetch event"""
        if task_module_request.data.get("data") == "SELECT_TOOLS":
            # Get available tools
            tools_by_server, available_tools = await self._get_available_tools()
            
            # Create an adaptive card for tool selection
            adaptive_card = {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Select the tools you want to use",
                        "weight": "bolder",
                        "size": "medium"
                    },
                    {
                        "type": "Input.ChoiceSet",
                        "id": "toolSelection",
                        "isMultiSelect": True,
                        "value": "",
                        "choices": [
                            {
                                "title": tool.name+": "+tool.description,
                                "value": tool.description
                            } for tool in available_tools
                        ]
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Select",
                        "data": {
                            "submitLocation": "toolSelectionSubmit"
                        }
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.3"
            }
            
            # Create a task module response with the adaptive card
            task_info = TaskModuleTaskInfo(
                card=CardFactory.adaptive_card(adaptive_card),
                title="Select Tools",
                height=500,
                width=400
            )
            
            return TaskModuleResponse(task=TaskModuleContinueResponse(value=task_info))
        
        return None
    
    async def on_teams_task_module_submit(
        self, turn_context: TurnContext, task_module_request: TaskModuleRequest
    ) -> TaskModuleResponse:
        """Handles the Teams task module submit event"""
        data = task_module_request.data
        
        if data.get("submitLocation") == "toolSelectionSubmit":
            selected_tools_str = data.get("toolSelection", "")
            
            # Parse the selected tools (comma-separated values if multiple are selected)
            if selected_tools_str:
                self._selected_tools = selected_tools_str.split(",")
            else:
                self._selected_tools = []
                
            # Initialize the agent with selected tools
            try:
                self._agent_cm = create_agent(self._selected_tools)
                self._agent = await self._agent_cm.__aenter__()
                tool_message = f"Agent initialized with {len(self._selected_tools)} tools: {', '.join(self._selected_tools)}" if self._selected_tools else "Agent initialized with all available tools"
                return TaskModuleResponse(task=TaskModuleMessageResponse(value=tool_message))
            except Exception as e:
                await turn_context.send_activity(f"Error initializing agent: {str(e)}")
                # Fall back to all tools
                self._agent_cm = create_agent()
                self._agent = await self._agent_cm.__aenter__()
                await turn_context.send_activity("Falling back to all available tools")
        
        return TaskModuleResponse(task=None)
    
    async def on_message_activity(self, turn_context: TurnContext):
        # If agent is not initialized, show the tool selection card
        if self._agent is None:
            await self.initialize_agent(turn_context)
            return
            
        # Process the message with the existing agent
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()

        res = await self._agent.ainvoke({"messages" : text})
        tool_calls = []
        for message in res["messages"]:
            if isinstance(message, ToolMessage):
                tool_calls.append({
                    "action name": message.name,
                    "content": message.content
                })
        response = res["messages"][-1].content
        await turn_context.send_activity(response)
        await turn_context.send_activity(json.dumps({"tool calls": tool_calls})) if len(tool_calls) else None
        return
