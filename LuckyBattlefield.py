import tkinter as tk
import random

# ---------- Constants ----------
GRID_SIZE = 8
BATTLE_WIDTH = 35
PLAYER_COL = 4
ENEMY_COL = 30

# ---------- Main Game ----------
class LuckyBattlefieldGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lucky Battlefield 2026.1")
        self.root.configure(bg="black")

        # ---------- DETECT SCREEN & SCALE ----------
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        scale = 0.8  # window will be 80% of screen size
        window_w = int(screen_w * scale)
        window_h = int(screen_h * scale)

        pos_x = (screen_w // 2) - (window_w // 2)
        pos_y = (screen_h // 2) - (window_h // 2)

        self.root.geometry(f"{window_w}x{window_h}+{pos_x}+{pos_y}")
        self.root.resizable(False, False)

        # ---------- Game state ----------
        self.game_state = "START"
        self.player = None
        self.enemies = []
        self.chests = []
        self.current_battle_enemy = None
        self.current_chest = None
        self.p_name = ""
        self.pos = [0, 0]
        self.map_pos = [0, 0]

        # ---------- Fonts ----------
        self.font_main = ("Courier New", max(12, window_h // 45), "bold")
        self.font_input = ("Courier New", max(10, window_h // 50))

        self.setup_ui()
        self.show_start_screen()

    # ---------- UI ----------
    def setup_ui(self):
        self.text_area = tk.Text(self.root, bg="black", fg="white", font=self.font_main,
                                 state="disabled", borderwidth=0, padx=40, pady=40)
        self.text_area.pack(expand=True, fill="both")
        self.text_area.tag_configure("red", foreground="#ff4444")
        self.text_area.tag_configure("green", foreground="#44ff44")
        self.text_area.tag_configure("white", foreground="white")
        self.text_area.tag_configure("select", background="#333", foreground="#44ff44")

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(self.root, textvariable=self.input_var, bg="#111",
                              fg="white", insertbackground="white", font=self.font_input)
        self.entry.pack(fill="x", side="bottom", padx=40, pady=20)
        self.entry.bind("<Return>", self.handle_input)
        self.entry.focus_set()

        self.root.bind("<Up>", lambda e: self.process_move(0,1))
        self.root.bind("<Down>", lambda e: self.process_move(0,-1))
        self.root.bind("<Left>", lambda e: self.process_move(-1,0))
        self.root.bind("<Right>", lambda e: self.process_move(1,0))
        self.root.bind("e", lambda e: self.toggle_inventory())
        self.root.bind("b", lambda e: self.toggle_data())

    # ---------- Write ----------
    def write(self,msg,tag="white"):
        self.text_area.config(state="normal")
        if msg=="CLEAR": self.text_area.delete("1.0",tk.END)
        else: self.text_area.insert(tk.END,msg,tag)
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)

    # ---------- Start ----------
    def show_start_screen(self):
        self.write("CLEAR")
        self.write("====================================\n")
        self.write("     LUCKY BATTLEFIELD 2026.1!     \n","green")
        self.write("====================================\n\n")
        self.write("Enter Hero Name and press Enter:\n")

    def handle_input(self,event):
        val = self.input_var.get().strip()
        self.input_var.set("")

        if self.game_state=="START":
            self.p_name = val if val else "Hero"
            self.game_state="AVATAR"
            self.write(f"\nWelcome, {self.p_name}!\nAvatar (1 character): ")
        elif self.game_state=="AVATAR":
            if len(val)==1:
                self.player = Player(self.p_name,val)
                self.game_state="LOADING_INIT"
                self.run_loading_bar("INITIATING BATTLEFIELD...",0,self.setup_complete)
            else:
                self.write("\nError! Use exactly 1 character: ")
        elif self.game_state=="BATTLE":
            self.process_battle_turn(val.upper())
        elif self.game_state=="CHEST":
            if val.upper()=="T": self.transfer_item()
            elif val.upper()=="Q":
                self.game_state="WORLD"
                self.render_world()
        elif self.game_state=="INVENTORY":
            if val.upper()=="Q":
                self.use_item()
                self.render_inventory()
        elif self.game_state=="DATA":
            if val.upper()=="B":
                self.game_state="WORLD"
                self.render_world()
        elif self.game_state=="GAMEOVER":
            if val.lower()=="r": self.restart_game()
            elif val.lower()=="q": self.root.destroy()

    # ---------- Loading ----------
    def run_loading_bar(self,label,step,callback):
        self.write("CLEAR")
        bar_len=20
        filled="="*step
        empty="-"*(bar_len-step)
        self.write(f"\n\n\n      {label}\n\n","green")
        self.write(f"      <{filled}{empty}>\n")
        if step<bar_len:
            self.root.after(50,lambda:self.run_loading_bar(label,step+1,callback))
        else:
            self.root.after(800,callback)

    # ---------- Restart ----------
    def restart_game(self):
        self.player=Player(self.p_name,self.player.symbol)
        self.enemies=[]
        self.chests=[]
        self.game_state="WORLD"
        self.setup_complete()

    # ---------- Setup ----------
    def setup_complete(self):
        self.run_loading_bar("SETTING THINGS UP...",0,self.enter_world)

    def enter_world(self):
        self.game_state="WORLD"
        self.enemies=[Enemy(self.player.level,[random.randint(0,7),random.randint(0,7)]) for _ in range(4)]
        self.chests=[Chest([random.randint(0,7),random.randint(0,7)]) for _ in range(3)]
        self.render_world()

    # ---------- Move ----------
    def process_move(self,dx,dy):
        if self.game_state not in ["WORLD","INVENTORY","CHEST"]: return
        if self.game_state=="WORLD":
            self.player.map_pos[0] += dx
            self.player.map_pos[1] += dy

            nx = self.player.pos[0] += dx
            ny = self.player.pos[1] += dy
            wrapped = False
            if ny < 0 or nx >= GRID_SIZE:
                nx = nx % GRID_SIZE
                wrapped = True
            if nx < 0 or ny >= GRID_SIZE:
                ny = ny % GRID_SIZE
                wrapped = True

            self.player.pos = [nx, ny]

            # Spawn new enemies/chests if wrapped
            if wrapped:
                self.enemies.append(Enemy(self.player.level,[random.randint(0,GRID_SIZE-1),random.randint(0,GRID_SIZE-1)]))
                self.chests.append(Chest([random.randint(0,GRID_SIZE-1),random.randint(0,GRID_SIZE-1)]))

            # Check for enemies
            for e in self.enemies:
                if e.pos==self.player.pos: self.start_battle(e); return
            # Check for chests
            for c in self.chests:
                if c.pos==self.player.pos: self.open_chest(c); return
            if self.player.map_pos == [7, 12]:
                self.start_final_boss(boss_type=1)
                return
            elif self.player.map_pos == [7, 27]:
                self.start_final_boss(boss_type=2)
                return
                
            self.render_world()
        elif self.game_state in ["INVENTORY","CHEST"]:
            if dx!=0: self.player.inv_idx=(self.player.inv_idx+dx)%9
            if dy!=0: self.player.inv_idx=(self.player.inv_idx-(dy*3))%9
            self.render_inventory() if self.game_state=="INVENTORY" else self.render_chest()

    # ---------- World ----------
    def render_world(self):
        self.write("CLEAR")
        p=self.player
        self.write(f"--- {p.name} Lv{p.level} ---\n","green")
        grid=[["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for c in self.chests: grid[c.pos[1]][c.pos[0]]="!"
        for e in self.enemies: grid[e.pos[1]][e.pos[0]]="E"
        if self.player.map_pos == [7, 12]:
            x,y = 7, 12
            grid_y = y % GRID_SIZE
            grid_x = x % GRID_SIZE
            grid[grid_y][grid_x] = "/"
        for y in range(GRID_SIZE-1,-1,-1):
            for x in range(GRID_SIZE):
                char,tag=grid[y][x],"white"
                if [x,y]==p.pos: char,tag=p.symbol,"green"
                elif char=="E": tag="red"
                elif char=="!": tag="green"
                self.write(f" {char} ",tag)
                if x<GRID_SIZE-1: self.write("|")
            self.write("\n")
        self.write(f"\nHP: {p.hp}/{p.max_hp} | XP: {p.xp}/100\n","green")
        self.write(f"[{p.map_pos[0]}, {p.map_pos[1]}]", "green")
        self.write("Arrows: Move | E: Inv | B: Stats\n")

    # ---------- Inventory ----------
    def toggle_inventory(self):
        if self.game_state=="WORLD":
            self.game_state="INVENTORY"
            self.render_inventory()
        elif self.game_state=="INVENTORY":
            self.game_state="WORLD"
            self.render_world()

    def render_inventory(self):
        self.write("CLEAR")
        p=self.player
        self.write(f"{p.name}'s Backpack\n","green")
        self.write(f"[{p.symbol}] (Arrows to select)\n" + "-"*30 + "\n")
        self.write("H:Heal | A:Atk | R:Res | W:Wpn | X:Armr\n\n")
        for i in range(9):
            tag="select" if i==p.inv_idx else "white"
            self.write(f" S{i+1}: {p.inventory[i]:<2} ",tag)
            if (i+1)%3==0: self.write("\n")
        self.write("\n[Q] Use/Equip | [E] Close")

    def use_item(self):
        item=self.player.inventory[self.player.inv_idx]
        if item=="S": return
        if item=="H": self.player.hp=min(self.player.max_hp,self.player.hp+60)
        elif item=="A": self.player.atk_mod+=random.randint(10,20)
        elif item=="R": self.player.df+=random.randint(5,15)
        elif item=="W": self.player.atk_mod+=random.randint(5,45)
        elif item=="X": self.player.df+=random.randint(5,45)
        self.player.inventory[self.player.inv_idx]="S"

    # ---------- Chests ----------
    def open_chest(self,chest):
        self.game_state="CHEST"
        self.current_chest=chest
        self.render_chest()

    def render_chest(self):
        self.write("CLEAR")
        self.write("=====================\n        CHEST        \n=====================\n","green")
        items_str = ", ".join(self.current_chest.items) if self.current_chest.items else "EMPTY"
        self.write(f"CHEST ITEMS: {items_str}\n\n")
        self.write("YOUR SLOTS:\n")
        for i in range(9):
            tag="select" if i==self.player.inv_idx else "white"
            self.write(f" S{i+1}: {self.player.inventory[i]:<2} ",tag)
            if (i+1)%3==0: self.write("\n")
        self.write("\n[T] Take Item | [Q] Exit")

    def transfer_item(self):
        if self.current_chest.items:
            item=self.current_chest.items.pop(0)
            self.player.inventory[self.player.inv_idx]=item
            self.render_chest()

    # ---------- Player Data ----------
    def toggle_data(self):
        if self.game_state=="WORLD":
            self.write("CLEAR")
            p=self.player
            self.write(f"--- PLAYER DATA ---\nName: {p.name}\nAvatar: {p.symbol}\nLevel: {p.level}\nXP: {p.xp}\nHP: {p.hp}/{p.max_hp}\nDF: {p.df}\nATK MOD: +{p.atk_mod}\n","green")
            self.write("\nPress 'B' to Return")
            self.game_state="DATA"
        elif self.game_state=="DATA":
            self.game_state="WORLD"
            self.render_world()

    # ---------- Battle ----------
    def start_battle(self,enemy):
        self.game_state="BATTLE"
        self.current_battle_enemy=enemy
        for a in self.player.attacks.values(): a['charge']=min(a['charge']+1,a['max'])
        self.render_battle()

    def render_battle(self,anim="",tag="white"):
        self.write("CLEAR")
        e,p=self.current_battle_enemy,self.player
        self.write(f"ENEMY Lv{e.level}  [{'='*int(max(0,e.hp)/e.max_hp*20):<20}]\n","red")
        self.write(f"{p.name} Lv{p.level}  [{'='*int(max(0,p.hp)/p.max_hp*20):<20}]\n\n","green")
        if anim: self.write(anim,tag)
        else:
            line=list(" "*BATTLE_WIDTH)
            line[PLAYER_COL],line[ENEMY_COL]=p.symbol,e.symbol
            self.write("".join(line))
        self.write("\n\n")
        for k,v in p.attacks.items():
            self.write(f"({k}) {v['name']:<10} [{'='*v['charge']}{'-'*(v['max']-v['charge'])}]\n","green")
        self.write("\n(A/S/F/U) or [M] Menu:")

    def start_final_boss(self,boss_type):
        self.saved_state = {
            'player': copy.deepcopy(self.player),
            'enemies': copy.deepcopy(self.enemies),
            'chests': copy.deepcopy(self.chests),
        }
        self.current_battle_enemy = FinalBoss(boss_type)
        self.game_state="BATTLE"

    def process_battle_turn(self,choice):
        if choice=='M': self.game_state="INVENTORY"; self.render_inventory(); return
        p,e=self.player,self.current_battle_enemy
        if choice not in p.attacks or p.attacks[choice]['charge']<p.attacks[choice]['max']: return
        atk=p.attacks[choice]
        p.attacks[choice]['charge']=0
        for a in p.attacks.values(): a['charge']=min(a['charge']+1,a['max'])
        dmg=int((atk['mult']*p.level)+p.atk_mod+random.randint(-30,30))
        hit=random.randint(1,10)>1
        self.animate_projectile(list(range(PLAYER_COL+1,ENEMY_COL)),atk['sym'],not hit,"green",
                                lambda:self.finish_player_hit(dmg,hit))

    def finish_player_hit(self,dmg,hit):
        e=self.current_battle_enemy
        if hit: e.hp-=dmg
        self.render_battle(f"HIT! {dmg} DMG" if hit else "MISS!","green")
        self.root.after(800,self.victory if e.hp<=0 else self.enemy_turn)

    def enemy_turn(self):
        e,p=self.current_battle_enemy,self.player
        dmg=max(1,(e.level*12)-p.df+random.randint(-5,5))
        hit=random.randint(1,10)>3
        self.animate_projectile(list(range(ENEMY_COL-1,PLAYER_COL,-1)),"-",not hit,"red",
                                lambda:self.finish_enemy_hit(dmg,hit))
        if isInstance(e, FinalBoss) and e.hp <= e.max_hp//2 and not e.beam_unlocked:
            e.beam_unlocked=True
            e.beam_length=1
            return
        if getattr(e,"beam_unlocked",False):
            e.beam_length += 1
            beam_line = "=" * e.beam_length
            self.render_battle(beam_line, "blue")
            if self.player.hp <= self.player.max_hp//20:
                self.player.symbol = f"({self.player.symbol})"
                
    def finish_enemy_hit(self,dmg,hit):
        if hit: self.player.hp-=dmg
        self.render_battle(f"ENEMY HIT! {dmg} DMG" if hit else "ENEMY MISS!","red")
        self.root.after(800,self.game_over if self.player.hp<=0 else self.render_battle)

    def animate_projectile(self,steps,sym,miss,tag,callback):
        def step_anim(idx):
            if idx>=len(steps): callback(); return
            line=list(" "*BATTLE_WIDTH)
            line[PLAYER_COL],line[ENEMY_COL]=self.player.symbol,self.current_battle_enemy.symbol
            line[steps[idx]]=sym if not (miss and idx>len(steps)//2) else "/"
            self.render_battle("".join(line),tag)
            self.root.after(25,lambda: step_anim(idx+1))
        step_anim(0)

    def victory(self):
        # XP gain based on enemy level +/- 20
        xp_gain = max(10, self.current_battle_enemy.level*10 + random.randint(-20,20))
        self.player.xp += xp_gain
        if self.player.xp>=100:
            self.player.level+=1
            self.player.xp=0
            self.player.max_hp+=50
            self.player.hp=self.player.max_hp
        if self.current_battle_enemy in self.enemies:
            self.enemies.remove(self.current_battle_enemy)
        self.game_state="WORLD"
        self.render_world()

    def victory(self):
        e=self.current_battle_enemy
        if isinstance(e, FinalBoss) and e.hp <= 0:
            self.write(f"{e.name} dropped a key!\n","blue")
            self.player.inventory[0] = "K"  # place in first slot
        super().victory()

    def game_over(self):
        self.game_state="GAMEOVER"
        self.write("CLEAR")
        self.write("===============================\n           GAME OVER           \n===============================\n","red")
        self.write(f"Name: {self.player.name}\nLevel: {self.player.level}\n[R] Restart | [Q] Quit")

# ---------- Player ----------
class Player:
    def __init__(self,name,symbol):
        self.name,self.symbol=name,symbol
        self.level,self.max_hp,self.hp,self.xp=1,150,150,0
        self.pos=[0,0]
        self.df,self.atk_mod=5,0
        self.inventory=["S"]*9
        self.inv_idx=0
        self.attacks={
            'A':{'name':'Attack','charge':1,'max':1,'mult':30,'sym':'-'},
            'S':{'name':'Special','charge':0,'max':3,'mult':50,'sym':'='},
            'F':{'name':'Fireball','charge':0,'max':5,'mult':75,'sym':'=>'},
            'U':{'name':'Ultra','charge':0,'max':8,'mult':100,'sym':'(=>)'}
        }

# ---------- Enemy ----------
class Enemy:
    def __init__(self,player_lvl,pos):
        self.level=random.randint(player_lvl,player_lvl+4)
        self.max_hp=100+self.level*50
        self.hp=self.max_hp
        self.pos=pos
        self.symbol="E"

# ---------- Chest ----------
class Chest:
    def __init__(self,pos):
        self.pos=pos
        pool=["H","A","R","W","X"]
        self.items=[random.choice(pool) for _ in range(random.randint(1,3))]

# --------- Final Boss ---------
class FinalBoss:
    def __init__(self, boss_type):
        if boss_type==1:
            self.name="Soul Phantom"
            self.hp=1750
            self.max_hp=1750
            self.symbol=">"
            self.color="blue"
            self.beam_unlocked=False
        else:
            self.name="Ultimate Void"
            self.hp=5000
            self.max_hp=5000
            self.symbol=";"
            self.color="blue"
            self.beam_unlocked=True

# ---------- Run ----------
if __name__=="__main__":
    root=tk.Tk()
    game=LuckyBattlefieldGUI(root)
    root.mainloop()

