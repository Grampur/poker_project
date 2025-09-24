"""
Range parser for processing preflop range data.
Handles parsing of hand ranges and calculating statistics.
"""

import re

class RangeParser:
    def __init__(self):
        # Define hand rankings for strength categorization
        self.premium_hands = {
            'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AQs', 'AJs', 'KQs', 'AKo'
        }
        self.strong_hands = {
            '99', '88', '77', 'ATs', 'A9s', 'A8s', 'KJs', 'KTs', 'QJs', 'QTs', 
            'JTs', 'T9s', '98s', 'AQo', 'AJo', 'ATo', 'KQo', 'KJo', 'QJo'
        }
    
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
                    # Convert specific hands to generic format
                    generic_hand = self.convert_to_generic_hand(hand)
                    if generic_hand:
                        range_dict[generic_hand] = frequency
                except ValueError:
                    continue
                    
        return range_dict
    
    def convert_to_generic_hand(self, specific_hand):
        """Convert specific hands like 'AcKd' to generic format like 'AKo'."""
        if len(specific_hand) != 4:
            return None
            
        rank1, suit1, rank2, suit2 = specific_hand[0], specific_hand[1], specific_hand[2], specific_hand[3]
        
        # Convert T to 10 for sorting, then back
        rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, '9': 9, '8': 8, 
                      '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        
        # Ensure higher rank comes first
        if rank_order.get(rank1, 0) < rank_order.get(rank2, 0):
            rank1, rank2 = rank2, rank1
            
        if rank1 == rank2:
            return f"{rank1}{rank2}"  # Pocket pair
        elif suit1 == suit2:
            return f"{rank1}{rank2}s"  # Suited
        else:
            return f"{rank1}{rank2}o"  # Offsuit
    
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
        if self.is_pocket_pair(hand):
            return 6  # 6 combinations for pocket pairs
        else:
            return 4 if self.is_suited(hand) else 12  # 4 for suited, 12 for offsuit
    
    def is_pocket_pair(self, hand):
        """Check if hand is a pocket pair."""
        return len(hand) == 2 and hand[0] == hand[1]
    
    def is_suited(self, hand):
        """Check if hand is suited."""
        return hand.endswith('s')
    
    def get_hand_strength(self, hand):
        """Categorize hand strength."""
        base_hand = hand.rstrip('so')  # Remove suit indicators
        if hand in self.premium_hands:
            return 'premium'
        elif hand in self.strong_hands:
            return 'strong'
        else:
            return 'marginal'
    
    def get_empty_stats(self):
        """Return empty statistics dictionary."""
        return {
            'total_combos': 0,
            'played_combos': 0,
            'vpip': 0,
            'pairs': 0,
            'suited': 0,
            'offsuit': 0,
            'premium': 0,
            'strong': 0,
            'marginal': 0
        }

    # Utility functions for the range grid
    def get_hand_matrix_position(self, hand):
        """Get the matrix position (row, col) for a hand in the 13x13 grid."""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        rank_to_idx = {rank: idx for idx, rank in enumerate(ranks)}
        
        if len(hand) < 2:
            return None
            
        rank1, rank2 = hand[0], hand[1]
        
        if rank1 not in rank_to_idx or rank2 not in rank_to_idx:
            return None
            
        r1_idx = rank_to_idx[rank1]
        r2_idx = rank_to_idx[rank2]
        
        if len(hand) == 2:  # Pocket pair
            return (r1_idx, r1_idx)
        elif hand.endswith('s'):  # Suited
            return (min(r1_idx, r2_idx), max(r1_idx, r2_idx))
        else:  # Offsuit
            return (max(r1_idx, r2_idx), min(r1_idx, r2_idx))
    
    def frequency_to_color(self, frequency):
        """Convert frequency to color for display."""
        if frequency >= 1.0:
            return "#006400"  # Dark green for always
        elif frequency >= 0.75:
            return "#228B22"  # Green for often
        elif frequency >= 0.5:
            return "#FFD700"  # Gold for sometimes
        elif frequency >= 0.25:
            return "#FFA500"  # Orange for rarely
        elif frequency > 0:
            return "#FFB6C1"  # Light pink for very rarely
        else:
            return "#FFFFFF"  # White for never