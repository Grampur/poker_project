"""
Range parser for processing preflop range data.
Handles parsing of hand ranges and calculating statistics.
"""

import re

class RangeParser:
    def __init__(self):
        pass
    
    def parse_range_line(self, line):
        """Parse a range line into hand-frequency pairs."""
        range_dict = {}
        
        if not line.strip():
            return range_dict
            
        # Split the line into hand_frequency pairs
        parts = line.split()
        
        for part in parts:
            if '_' in part:
                # Format: hand_frequency (e.g., "2s2h_1", "Ac5c_0.75")
                hand, freq_str = part.rsplit('_', 1)
                try:
                    frequency = float(freq_str)
                    range_dict[hand] = frequency
                except ValueError:
                    continue
                    
        return range_dict
    
    def calculate_range_statistics(self, range_data):
        """Calculate statistics for a given range."""
        if not range_data:
            return self.get_empty_stats()
            
        total_combos = 0
        played_combos = 0
        
        # Hand category counters
        pairs = 0
        suited = 0
        offsuit = 0
        
        # Strength categories
        premium = 0
        strong = 0
        marginal = 0
        
        for hand, frequency in range_data.items():
            if frequency <= 0:
                continue
                
            # Count combos (simplified - assumes each hand represents standard combos)
            hand_combos = self.get_hand_combos(hand)
            total_combos += hand_combos
            played_combos += hand_combos * frequency
            
            # Categorize hand types
            if self.is_pocket_pair(hand):
                pairs += hand_combos * frequency
            elif self.is_suited(hand):
                suited += hand_combos * frequency
            else:
                offsuit += hand_combos * frequency
                
            # Categorize by strength
            strength = self.get_hand_strength(hand)
            if strength == 'premium':
                premium += hand_combos * frequency
            elif strength == 'strong':
                strong += hand_combos * frequency
            else:
                marginal += hand_combos * frequency
        
        # Calculate percentages
        total_possible = 1326  # Total poker hand combinations
        vpip = (played_combos / total_possible) * 100 if total_possible > 0 else 0
        
        if played_combos > 0:
            pairs_pct = (pairs / played_combos) * 100
            suited_pct = (suited / played_combos) * 100
            offsuit_pct = (offsuit / played_combos) * 100
            premium_pct = (premium / played_combos) * 100
            strong_pct = (strong / played_combos) * 100
            marginal_pct = (marginal / played_combos) * 100
        else:
            pairs_pct = suited_pct = offsuit_pct = 0
            premium_pct = strong_pct = marginal_pct = 0
        
        return {
            'total_combos': int(total_combos),
            'played_combos': int(played_combos),
            'vpip': vpip,
            'pairs': pairs_pct,
            'suited': suited_pct,
            'offsuit': offsuit_pct,
            'premium': premium_pct,
            'strong': strong_pct,
            'marginal': marginal_pct
        }
    
    def get_hand_combos(self, hand):
        """Get number of combinations for a hand."""
        