# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json

from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from langchain_core.messages.tool import ToolMessage

from mcp_client import create_agent

class TeamsMcpClientAgent(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str, mcp_servers_file_path) -> None:
        self._app_id = app_id
        self._app_password = app_password
        self._agent = None
        self._agent_cm = None
        self._mcp_servers_file_path = mcp_servers_file_path
        
    async def _initialize_agent(self, turn_context: TurnContext):
        """Initialize the agent if it hasn't been initialized yet"""
        if self._agent is None:
            self._agent_cm = create_agent(self._mcp_servers_file_path, turn_context)
            self._agent = await self._agent_cm.__aenter__()

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: [TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"Welcome { member.given_name } { member.surname }. "
                )
                if self._agent is None:
                    await self._initialize_agent(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        # Initialize agent if needed
        if self._agent is None:
            await self._initialize_agent(turn_context)
            
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
        # show tool calls, only for demo purpose
        await turn_context.send_activity(json.dumps({"tool calls": tool_calls})) if len(tool_calls) else None
        return
