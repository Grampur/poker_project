"""
Solution loader for parsing poker solution files.
Handles loading and parsing of the solution text files.
"""

import os
import re
from .range_parser import RangeParser

class SolutionLoader:
    def __init__(self):
        self.range_parser = RangeParser()
        
    def scan_solutions_folder(self, folder_path):
        """Scan the solutions folder and return available data."""
        available_data = {
            'stacks': set(),
            'scenarios': set(),
            'stack_scenarios': {},
            'scenario_boards': {}
        }
        
        if not os.path.exists(folder_path):
            return available_data
            
        try:
            # Walk through the directory structure
            for stack_dir in os.listdir(folder_path):
                stack_path = os.path.join(folder_path, stack_dir)
                if not os.path.isdir(stack_path):
                    continue
                    
                # Extract stack size (assuming format like "11", "14", etc.)
                if stack_dir.isdigit():
                    stack = stack_dir
                    available_data['stacks'].add(stack)
                    available_data['stack_scenarios'][stack] = []
                    
                    # Look for scenario folders
                    for scenario_dir in os.listdir(stack_path):
                        scenario_path = os.path.join(stack_path, scenario_dir)
                        if not os.path.isdir(scenario_path):
                            continue
                            
                        available_data['scenarios'].add(scenario_dir)
                        available_data['stack_scenarios'][stack].append(scenario_dir)
                        
                        # Look for board files
                        key = f"{stack}_{scenario_dir}"
                        available_data['scenario_boards'][key] = []
                        
                        for file_name in os.listdir(scenario_path):
                            if file_name.endswith('.txt'):
                                board = file_name[:-4]  # Remove .txt extension
                                available_data['scenario_boards'][key].append(board)
                                
        except Exception as e:
            print(f"Error scanning solutions folder: {e}")
            
        return available_data
    
    def load_solution(self, file_path):
        """Load a solution file and parse it."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Solution file not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return self.parse_solution_content(content)
            
        except Exception as e:
            raise Exception(f"Error loading solution file: {e}")
    
    def parse_solution_content(self, content):
        """Parse the solution file content."""
        solution = {
            'game_info': {},
            'oop_range': {},
            'ip_range': {},
            'decision_tree': {}
        }
        
        lines = content.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse game information
            if line.startswith('game = '):
                solution['game_info'] = self.parse_game_info(line)
                continue
                
            # Identify sections
            if line == 'OOP preflop range':
                current_section = 'oop_range'
                continue
            elif line == 'IP preflop range':
                current_section = 'ip_range'
                continue
            elif line.startswith('root,') or line.startswith('1 check,') or line.startswith('2 bet'):
                current_section = 'decision_tree'
                continue
                
            # Parse range data
            if current_section == 'oop_range':
                solution['oop_range'] = self.range_parser.parse_range_line(line)
            elif current_section == 'ip_range':
                solution['ip_range'] = self.range_parser.parse_range_line(line)
            elif current_section == 'decision_tree':
                # Store decision tree data (for future use)
                if line and not line.startswith('root,'):
                    solution['decision_tree'][current_section] = line
                    
        return solution
    
    def parse_game_info(self, line):
        """Parse the game information line."""
        game_info = {}
        
        # Example: game = '3-max Tournament', preflop situation = 'BU openraise BB call', stack = '9', pot = '4', bets = '33 50 75 100 225'
        parts = line.split(', ')
        
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                game_info[key] = value
                
        return game_info