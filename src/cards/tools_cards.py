# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
from botbuilder.core import CardFactory
from botbuilder.schema import CardAction, HeroCard
from botbuilder.schema.teams import TaskModuleTaskInfo, TaskModuleContinueResponse

class ToolsSelectionCard:
    """Class for handling the tools selection card and task modules"""
    
    @staticmethod
    def create_tools_selection_card():
        """Create a card with buttons for tool selection and showing selected tools"""
        buttons = [
            CardAction(
                type="invoke",
                title="Select Tools",
                value={"type": "task/fetch", "data": "SELECT_TOOLS"}
            ),
            CardAction(
                type="invoke",
                title="Show Selected Tools",
                value={"type": "task/fetch", "data": "SHOW_TOOLS"}
            )
        ]
        
        return HeroCard(
            title="Agent Initialization",
            text="The agent needs to be initialized with tools. Would you like to select specific tools?",
            buttons=buttons
        )
    
    @staticmethod
    def create_tools_selection_task_module(tools_by_server):
        """Create a task module for selecting tools from a hierarchical structure"""
        card_items = []
        
        # Add header
        card_items.append({
            "type": "TextBlock",
            "text": "Select the tools you want to use",
            "weight": "bolder",
            "size": "medium",
            "wrap": True
        })
        
        # Create hierarchical structure
        for server_name, tools in tools_by_server.items():
            # Add server header as a collapsible container
            server_container = {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [
                                    {
                                        "type": "Input.Toggle",
                                        "id": f"server_{server_name}",
                                        "title": f'{server_name}',
                                        "valueOn": "true",
                                        "valueOff": "false",
                                        "value": "false"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            card_items.append(server_container)
            
            # Add tools for this server
            tool_choices = []
            for tool in tools:
                tool_choices.append({
                    "title": f"{tool['name']} - {tool['description']}",
                    "value": tool['full_name']
                })
            
            # Add a choice set for tools within this server
            tool_choice_set = {
                "type": "Container",
                "items": [
                    {
                        "type": "Input.ChoiceSet",
                        "id": f"tools_{server_name}",
                        "isMultiSelect": True,
                        "choices": tool_choices,
                        "style": "expanded",
                        "wrap": True
                    }
                ],
                "spacing": "none",
                "style": "default",
                "padding": "0px, 0px, 0px, 40px"  # Add left padding for indent
            }
            card_items.append(tool_choice_set)
        
        # Create an adaptive card with the hierarchical structure
        adaptive_card = {
            "type": "AdaptiveCard",
            "body": card_items,
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Apply",
                    "data": {
                        "submitLocation": "toolSelectionSubmit"
                    }
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5"
        }
        
        # Create a task module response with the adaptive card
        task_info = TaskModuleTaskInfo(
            card=CardFactory.adaptive_card(adaptive_card),
            title="Select Tools",
            height=600,
            width=500
        )
        
        return TaskModuleContinueResponse(value=task_info)
    
    @staticmethod
    def create_show_tools_task_module(selected_tools, agent_initialized=True):
        """Create a task module to show the currently selected tools"""
        card_items = []
        
        # Add header
        card_items.append({
            "type": "TextBlock",
            "text": "Currently Selected Tools",
            "weight": "bolder",
            "size": "medium",
            "wrap": True
        })
        
        # Check if agent is initialized
        if not agent_initialized:
            card_items.append({
                "type": "TextBlock",
                "text": "Agent is not initialized yet. Please select tools to initialize the agent.",
                "wrap": True
            })
        elif not selected_tools or len(selected_tools) == 0:
            # No tools selected
            card_items.append({
                "type": "TextBlock",
                "text": "No specific tools are selected. The agent is using all available tools.",
                "wrap": True
            })
        else:
            # Group tools by server for display
            tools_by_server = {}
            for tool_name in selected_tools:
                # Extract server name from tool name (format: "server.tool")
                parts = tool_name.split(".", 1)
                if len(parts) == 2:
                    server_name, tool = parts
                    if server_name not in tools_by_server:
                        tools_by_server[server_name] = []
                    tools_by_server[server_name].append(tool)
            
            # Display tools grouped by server
            for server_name, tools in tools_by_server.items():
                # Add server header
                card_items.append({
                    "type": "TextBlock",
                    "text": f"**{server_name}**",
                    "wrap": True,
                    "spacing": "medium"
                })
                
                # Add tools list
                tool_list = "\n".join([f"- {tool}" for tool in tools])
                card_items.append({
                    "type": "TextBlock",
                    "text": tool_list,
                    "wrap": True
                })
        
        # Create an adaptive card with the selected tools
        adaptive_card = {
            "type": "AdaptiveCard",
            "body": card_items,
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Close",
                    "data": {
                        "submitLocation": "closeSelectedTools"
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "Select Tools",
                    "data": {
                        "submitLocation": "goToSelectTools",
                        "action": "SELECT_TOOLS"
                    }
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.5"
        }
        
        # Create a task module response with the adaptive card
        task_info = TaskModuleTaskInfo(
            card=CardFactory.adaptive_card(adaptive_card),
            title="Selected Tools",
            height=400,
            width=400
        )
        
        return TaskModuleContinueResponse(value=task_info)
