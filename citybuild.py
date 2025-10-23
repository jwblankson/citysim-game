import os
import random
import time

def refresh_display():
    """Refresh the console output for seamless visualization"""
    os.system('cls' if os.name == 'nt' else 'clear')

class Structure:
    """Defines a structure including its form, icon, and impacts"""
    def __init__(self, struct_type, row, col):
        self.row, self.col = row, col
        if struct_type == 'residence':
            self.label = 'RESIDENCE'
            self.icon, self.height, self.width = '#', 2, 3
            self.inhabitants, self.income = 15, -300
        elif struct_type == 'pathway':
            self.label = 'PATHWAY'
            self.icon, self.height, self.width = '═', 1, 6
            self.inhabitants, self.income = 0, -150
        elif struct_type == 'stream':
            self.label = 'STREAM'
            self.icon, self.height, self.width = '~', 4, 2
            self.inhabitants, self.income = -5, -400
        elif struct_type == 'plant':
            self.label = 'PLANT'
            self.icon, self.height, self.width = '▓', 2, 4
            self.inhabitants, self.income = -10, 1000
        elif struct_type == 'green':
            self.label = 'GREEN'
            self.icon, self.height, self.width = '☘', 2, 2
            self.inhabitants, self.income = 20, 0

def setup_city():
    """Set up the initial city environment"""
    dimension = int(input("Specify urban area size (8-20): "))
    map_layout = [['.' for _ in range(dimension)] for _ in range(dimension)]
    return dimension, map_layout, [], 20, 50000

def display_guide():
    """Present the introductory instructions"""
    print("\n" + "="*65)
    print("  URBANPLANNER™ - CONSTRUCT YOUR IDEAL METROPOLIS!  ")
    print("="*65)
    print("RULES:")
    print("• Input 'row column' → Decide on construction!")
    print("  1. RESIDENCE # (2x3 YELLOW): +15res -300fund")
    print("  2. PATHWAY  ═ (1x6 GRAY):   -150fund")
    print("  3. STREAM ~ (4x2 BLUE):   -5res -400fund")
    print("  4. PLANT  ▓ (2x4 GRAY): +1000fund -10res")
    print("  5. GREEN  ☘ (2x2 GREEN):  +20res 0fund")
    print("\n• Select BUILT → DESTROY to 'x' MARK")
    print("• 'h' = ASSIST | 'q' = EXIT")
    print("\nHAZARDS: BLAZE propagates via residences | DELUGE targets residences/pathways")
    print("Hit ENTER to begin...")
    input()

def render_map(map_layout, funds, residents):
    """Render the map with vibrant backgrounds (ESSENTIAL)"""
    palette = {'.': '\033[42m', '#': '\033[43m', '═': '\033[47m', '~': '\033[44m', 
               '▓': '\033[100m', '☘': '\033[102m', 'x': '\033[41m'}
    clear = '\033[0m'
    
    # Solid green frame
    print('\033[42m' + '═' * (len(map_layout[0])*2 + 4) + clear)
    
    for line in map_layout:
        segment = '\033[42m  ' + clear  # Green side margin
        for tile in line:
            segment += palette.get(tile, clear) + tile
        print(segment + clear + '  \033[42m' + clear)  # Green side margin
    
    print('\033[42m' + '═' * (len(map_layout[0])*2 + 4) + clear)
    print(f"\033[41mFUNDS: ${funds:,}  RES: {residents}\033[0m")

def display_assist():
    """In-game assistance summary"""
    print("\nRAPID GUIDE")
    print("• '3 4' → Target position")
    print("• Select: 1=RESIDENCE, 2=PATHWAY, 3=STREAM, 4=PLANT, 5=GREEN")
    print("• Target existing → WIPE OUT full entity")
    print("• BLAZE: Advances thru RESIDENCES, halted by pathways/greens")
    print("• DELUGE: STREAMS assault RESIDENCES & PATHWAYS")
    print("ADVICE: Lay pathways initially, shield residences!")

def validate_position(pos_input, dimension):
    """Validate position input with error handling - retries on failure"""
    while True:
        try:
            tokens = pos_input.strip().split()
            if len(tokens) != 2: raise ValueError
            row, col = int(tokens[0]), int(tokens[1])
            if not (0 <= row < dimension and 0 <= col < dimension):
                print(f"\033[91mBeyond urban limits! Range 0-{dimension-1}\033[0m")
                return None
            return row, col
        except:
            print("\033[91mWrong format! Apply '3 4'\033[0m")
            pos_input = input("Retry: ")

def present_construct_options(row, col, dimension):
    """Present construction choices with spatial details"""
    vert_space = dimension - row
    horiz_space = dimension - col
    print(f"\nCONSTRUCT OPTIONS at ({row},{col})")
    print(f"  Vertical space: {vert_space} | Horizontal space: {horiz_space}")
    print("  1. RESIDENCE # (2x3) → requires 2 vert, 3 horiz")
    print("  2. PATHWAY  ═ (1x6) → requires 1 vert,  6 horiz")
    print("  3. STREAM ~ (4x2) → requires 4 vert, 2 horiz")
    print("  4. PLANT  ▓ (2x4) → requires 2 vert, 4 horiz")
    print("  5. GREEN  ☘ (2x2) → requires 2 vert, 2 horiz")
    while True:
        selection = input("Pick (1-5): ").strip()
        if selection in ['1','2','3','4','5']:
            return ['residence','pathway','stream','plant','green'][int(selection)-1]
        print("\033[91mSelect 1-5!\033[0m")

def check_clear_zone(map_layout, row, col, height, width, dimension):
    """Verify zone availability for construction"""
    if row + height > dimension or col + width > dimension: return False
    for vert in range(row, row + height):
        for horiz in range(col, col + width):
            if map_layout[vert][horiz] not in ['.', 'x']:
                return False
    return True

def construct_or_remove(map_layout, structures, row, col, residents, funds, dimension):
    """Manage construction OR removal operations"""
    # Prioritize removal check
    for struct in structures[:]:
        if row >= struct.row and row < struct.row + struct.height and \
           col >= struct.col and col < struct.col + struct.width:
            # Erase complete structure
            for vert in range(struct.row, struct.row + struct.height):
                for horiz in range(struct.col, struct.col + struct.width):
                    map_layout[vert][horiz] = 'x'
            residents -= struct.inhabitants
            funds -= struct.income
            structures.remove(struct)
            print(f"\033[91mREMOVED {struct.label}!\033[0m")
            print(f"   RES -{struct.inhabitants}  FUND -{struct.income}")
            return residents, funds, False
    
    # Proceed to construction
    struct_type = present_construct_options(row, col, dimension)
    struct = Structure(struct_type, row, col)
    
    if not check_clear_zone(map_layout, row, col, struct.height, struct.width, dimension):
        print(f"\033[91mInsufficient area! {struct_type.upper()} demands {struct.height}x{struct.width}\033[0m")
        return residents, funds, True  # Retry flag
    
    # Deploy structure
    for vert in range(row, row + struct.height):
        for horiz in range(col, col + struct.width):
            map_layout[vert][horiz] = struct.icon
    structures.append(struct)
    residents += struct.inhabitants
    funds += struct.income
    
    print(f"\033[92mCONSTRUCTED {struct.label} ({struct.height}x{struct.width})!\033[0m")
    print(f"   RES +{struct.inhabitants}  FUND {struct.income}")
    return residents, funds, False

def blaze_event(map_layout, structures, residents, funds):
    """Simulated BLAZE event - propagates across residences"""
    print("\033[91mBLAZE EMERGENCY! Observe propagation...\033[0m")
    time.sleep(0.5)
    
    residences = [(i,j) for i in range(len(map_layout)) for j in range(len(map_layout)) if map_layout[i][j] == '#']
    if not residences:
        print("\033[92mNo residences affected - metropolis secure!\033[0m")
        return residents, funds
    
    init_row, init_col = random.choice(residences)
    pending = [(init_row, init_col)]
    obliterated = 0
    
    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    blocks = {'═', '~', '▓', '☘', '.', 'x'}
    
    while pending:
        row, col = pending.pop(0)
        if map_layout[row][col] != '#': continue
        
        map_layout[row][col] = 'x'
        refresh_display()
        render_map(map_layout, funds, residents)
        print("\033[91mIgniting...\033[0m")
        time.sleep(0.3)
        obliterated += 1
        
        for drow, dcol in offsets:
            nrow, ncol = row + drow, col + dcol
            if (0 <= nrow < len(map_layout) and 0 <= ncol < len(map_layout) and 
                map_layout[nrow][ncol] == '#' and map_layout[nrow][ncol] not in blocks):
                pending.append((nrow, ncol))
    
    for struct in structures[:]:
        if struct.icon == '#':
            residents -= struct.inhabitants
            funds -= struct.income
            structures.remove(struct)
            break
    
    print(f"\033[93mBLAZE obliterated {obliterated} residences!\033[0m")
    return residents, funds

def deluge_event(map_layout, structures, residents, funds):
    """Simulated DELUGE event - assaults residences and pathways"""
    print("\033[94mDELUGE ALERT! Streams surging...\033[0m")
    time.sleep(0.5)
    
    streams = [(i,j) for i in range(len(map_layout)) for j in range(len(map_layout)) if map_layout[i][j] == '~']
    if not streams:
        print("\033[92mNo streams active - metropolis secure!\033[0m")
        return residents, funds
    
    init_row, init_col = random.choice(streams)
    pending = [(init_row, init_col)]
    obliterated = 0
    
    offsets = [(-1,0), (1,0), (0,-1), (0,1)]
    victims = {'#', '═'}
    
    while pending:
        row, col = pending.pop(0)
        if map_layout[row][col] not in victims: continue
        
        map_layout[row][col] = 'x'
        refresh_display()
        render_map(map_layout, funds, residents)
        print("\033[94mInundating...\033[0m")
        time.sleep(0.3)
        obliterated += 1
        
        for drow, dcol in offsets:
            nrow, ncol = row + drow, col + dcol
            if (0 <= nrow < len(map_layout) and 0 <= ncol < len(map_layout) and 
                map_layout[nrow][ncol] in victims):
                pending.append((nrow, ncol))
    
    print(f"\033[93mDELUGE obliterated {obliterated} entities!\033[0m")
    return residents, funds

def core_loop():
    """Primary simulation cycle - limit to 9 lines!"""
    dimension, map_layout, structures, residents, funds = setup_city()
    display_guide()
    
    while True:
        refresh_display()
        render_map(map_layout, funds, residents)
        
        if random.random() < 0.12:
            event = random.choice(['blaze', 'deluge'])
            if event == 'blaze':
                residents, funds = blaze_event(map_layout, structures, residents, funds)
            else:
                residents, funds = deluge_event(map_layout, structures, residents, funds)
            input("\033[92mReconstruct! Hit ENTER...\033[0m")
            continue
        
        position = input("\033[93mNext action! Input row column (or q/h): \033[0m")
        if position.lower() == 'q': break
        if position.lower() == 'h': 
            display_assist()
            input("\033[92mHit ENTER...\033[0m")
            continue
        
        row, col = validate_position(position, dimension)
        if row is None: 
            input("\033[92mHit ENTER...\033[0m")
            continue
            
        residents, funds, retry = construct_or_remove(map_layout, structures, row, col, residents, funds, dimension)
        if retry:
            input("\033[92mHit ENTER to attempt again...\033[0m")
        else:
            input("\033[92mAdvance! Hit ENTER...\033[0m")

if __name__ == "__main__":
    core_loop()
