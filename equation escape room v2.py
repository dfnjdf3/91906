# Name: Jai Irudayarajan
# Date: 16/05/2025
# Purpose: to create a complex maths quiz.

import tkinter as tk
from tkinter import messagebox # To use pop up messagebox,
import os
from PIL import Image, ImageTk # To use images.
import random
import math
from fractions import Fraction
import time
import pygame # To add sound in the quiz.
from fpdf import FPDF
from tkinter import filedialog

pygame.mixer.init() # Pygame mixer to playback the sound effect.


correct_sound_location="assets/correct-156911.mp3" # Load correct sound from the folder.
wrong_sound_location="assets/wrong-47985.mp3" # Load wrong sound from the folder.
try:
    sound_correct=pygame.mixer.Sound("assets/correct-156911.mp3") # Give the location of the sound a value.
except Exception as e:
    print(f"There is a problem loading the correct sound") # Print in terminal if the sound is not loading.
    sound_correct=None # Giving the correct sound a value.
try:
    sound_wrong=pygame.mixer.Sound("assets/wrong-47985.mp3") # Give the location of the sound a value.
except Exception as e:
    print(f"There is a problem loading the wrong sound") # Print in terminal if the sound is not loading.
    sound_wrong=None # Giving the wrong sound a value.


#Global variables

final_geo_point=None # Gives a value to geometry point.
player_name="" # Sets the player name as nothing until the player types their name.
Name_entry=None # Sets a entry for the players name.
canvas=None # This create a canvas for the main gui only.
image_background=None # Sets the background as nothing until i set it.

width_window=800 # Sets the width of the window as 800.
height_window=800 # Sets the height of the window as 800.

start_game_image=None
instructions_image=None
exit_image=None
progress_image=None

Start_game_id=None # Sets a varible for my start game button image.
instructions_id=None # Sets a varible for my instruction button image.
exit_id=None # Sets a varible for my exit game button image.
progress_id=None # Sets a varible for my progress button image.



player_statistics={} # Creates a dictionary to save the the overall score for each player like the name, puzzels sovled, mazes completed, and overall time the player took to finish the maze.

Asset_direction="assets"
progress_txt_file="player_score.txt"
# Function for image location.
def get_image_location(namefile): # Makes a location to the image file.
    return os.path.join("assets", namefile)
def coordinate_normalize_entry(text):
    text=text.replace(" ", "").replace("(", "").replace(")", "") # Gives a value to the function text.
    parts=text.split(",") # Gives a value to parts.
    if len(parts)==2:
        try:
            x=int(parts[0]) # Gives a value to x.
            y=int(parts[1]) # Gives a value to y.
            return f"({x},{y})"
        except:
            return None
    return None

#Progress handling
def progress_load():
    global player_statistics
    player_statistics={}
    if os.path.exists(progress_txt_file):
        try:
            with open(progress_txt_file, 'r') as f:
                for line in f:
                    parts=line.strip().split(',') # To help old 3part and new 4part lines.
                    if len(parts)==3 or len(parts)==4:
                        name=parts[0]
                        puzzles_completed=int(parts[1])
                        mazes_done=int(parts[2])
                        Fastest_time=None
                        if len(parts)==4:
                            try:
                                Fastest_time=float(parts[3])
                            except ValueError:
                                Fastest_time=None
                        player_statistics[name]={
                            'puzzles_completed':puzzles_completed,
                            'mazes_done':mazes_done,
                            'Fastest_time':Fastest_time
                        }
        except Exception as e:
            messagebox.showerror("Error loading progress", f"Can not load player data: {e}")# Gives and error as popup window if the player date can not load.
            player_statistics={}# Factory reset to being empty if their is an error.

def progress_save(): # Making a funtion to save the player progress.
    global player_statistics
    try:
        with open(progress_txt_file, 'w') as f:
            for name, stats in player_statistics.items():
                Fastest_time_value=stats.get('Fastest_time')
                if Fastest_time_value is None:
                    f.write(f"{name}, {stats['puzzles_completed']}, {stats['mazes_done']}\n")
                else:
                    f.write(f"{name}, {stats['puzzles_completed']}, {stats['mazes_done']}, {Fastest_time_value}\n")
    except Exception as e:
        messagebox.showerror("Progress Can not be saved", f"Not able to save the players progress: {e}") # Gives an error message if can not load player progress.

def autoupdate_player_progress_overall(player_name, added_puzzels=0, added_mazes=0, taken_time=None): # Creates functions to automacticlly save player data and their name.
    if player_name not in player_statistics:
        player_statistics[player_name]={'puzzles_completed': 0, 'mazes_done': 0, 'Fastest_time': None}
    player_statistics[player_name]['puzzles_completed']+=added_puzzels
    player_statistics[player_name]['mazes_done']+=added_mazes
    if taken_time is not None:
        best_current=player_statistics[player_name].get('Fastest_time')# Creates a value to get the fastest time.
        if best_current is None or taken_time<best_current:
            player_statistics[player_name]['Fastest_time']=taken_time
    progress_save()# Saves the progress ASAP.

def bg_setup():
    global canvas, image_background
    try:
        img=Image.open(get_image_location("resized_image.png"))# Making sure to use my default bg image.
        img=img.resize((width_window, height_window), Image.Resampling.LANCZOS)
        image_background=ImageTk.PhotoImage(img)
    except FileNotFoundError:
        messagebox.showerror("Photo Error", f"Background photo not found in get_image('resized_image.png'). Please make sure to check the filename and the location of the file")
        main_gui.destroy()
        return
    except Exception as e:
        messagebox.showerror("Photo Error", f"Can not load image, check if image is broken/corrupted: {e}")
        main_gui.destroy()
        return
    main_gui.geometry(f"{width_window}x{height_window}")
    if canvas: # Only when the canvas is made, it will destroy the previous window before creating a new window.
        canvas.destroy()
    canvas=tk.Canvas(main_gui, width=width_window, height=height_window)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=image_background, anchor="nw")

def reset_main_gui(): # Creates a function to reset the main window.
    if hasattr(main_gui, 'maze_game_gui') and main_gui.maze_game_gui.maze_gui.winfo_exists():
        main_gui.maze_game_gui.maze_gui.destroy() # Makes sure to close/destroy the maze window and is not the main gui.
    main_gui.deiconify() # Ensures that the main gui is seeable.
    for widget in main_gui.winfo_children():
        widget.destroy()
    bg_setup()
    main_gui_setup()

def control_button_click_canvas(event, action_func): # When the image button is clicked in my main menu.
    action_func()
def main_gui_setup():
    global Name_entry, start_game_image, instructions_image, exit_image, progress_image
    global Start_game_id, instructions_id, exit_id, progress_id

    try:
        # Load all the button images.
        start_game_image = ImageTk.PhotoImage(Image.open(get_image_location("start_game_button2.png")))

        instructions_image = ImageTk.PhotoImage(Image.open(get_image_location("instructions_button3.png")))

        exit_image = ImageTk.PhotoImage(Image.open(get_image_location("exit_button2.png")))

        progress_image = ImageTk.PhotoImage(Image.open(get_image_location("progress_button2.png")))

    except Exception as e:
        messagebox.showerror("Photo error", f"Cannot load one or more button images: {e}")
        return

    # Draw title and entry field.
    canvas.create_text(width_window / 2, 100, text="The Equation Escape Room", font=("Helvetica", 24, "bold"), fill="#f9e4bc")
    canvas.create_text(width_window / 2, 160, text="Enter your Name:", font=("Helvetica", 16, "bold"), fill="#f9e4bc")
    Name_entry = tk.Entry(main_gui, font=("Helvetica", 14), width=30)
    canvas.create_window(width_window / 2, 190, window=Name_entry)
    Name_entry.focus_set()

    # Button spacing setup.
    height_entry = Name_entry.winfo_reqheight() or 28  # Fallback if not yet rendered.
    y_start = 190 + height_entry + 40  # Starting Y position after name entry.
    vertical_gap = 80  # Space between buttons.

    # Start Game Button.
    Start_game_id = canvas.create_image(width_window / 2, y_start, image=start_game_image, anchor="center")
    canvas.tag_bind(Start_game_id, "<Button-1>", lambda e: control_button_click_canvas(e, start_game))

    # Instructions Button.
    y_instructions = y_start + vertical_gap
    instructions_id = canvas.create_image(width_window / 2, y_instructions, image=instructions_image, anchor="center")
    canvas.tag_bind(instructions_id, "<Button-1>", lambda e: control_button_click_canvas(e, show_instructions))

    # Progress Button.
    y_progress = y_instructions + vertical_gap
    progress_id = canvas.create_image(width_window / 2, y_progress, image=progress_image, anchor="center")
    canvas.tag_bind(progress_id, "<Button-1>", lambda e: control_button_click_canvas(e, progress_show))

    # Exit Button.
    y_exit = y_progress + vertical_gap
    exit_id = canvas.create_image(width_window / 2, y_exit, image=exit_image, anchor="center")
    canvas.tag_bind(exit_id, "<Button-1>", lambda e: control_button_click_canvas(e, game_exit))


def start_game():# To start the Game and check if the user has entered their name.
    global player_name
    if Name_entry is None:
        messagebox.showerror("Error", "Enter your name entry field")
        return
    player_name=Name_entry.get().strip()
    if not player_name:
        messagebox.showerror("Entry Problem", "Please kindly enter your name before starting the game")
    else:
        modes_maths_show(player_name)

def modes_maths_show(player_name):# Lists the the topics as buttons.
    for widget in main_gui.winfo_children():
        widget.destroy()
    bg_setup()
    canvas.create_text(width_window / 2, 100, text=f"Choose a Math subject, {player_name}", font=("Helvetica", 16), fill="#f9e4bc")
    topics=["Calculus", "Algebra", "Geometry", "Exponents", "Fractions", "Number Theory"]
    y=150
    for topic in topics:
        BTN=tk.Button(main_gui, text=topic, width=20, font=("Helvetica", 12),
                          command=lambda m=topic: select_level(m))
        canvas.create_window(width_window / 2, y, window=BTN)
        y += 40

    button_return=tk.Button(main_gui, text="Go back to Main menu", width=20, font=("Helvetica", 12), command=reset_main_gui)
    canvas.create_window(width_window / 2, y +20, window=button_return)


def select_level(topic):# When the user chooses the topic they can choose what mode to play.
    for widget in main_gui.winfo_children():
        widget.destroy()
    bg_setup()
    canvas.create_text(width_window / 2, 100, text=f"{topic} Mode: Choose level of Difficulty", font=("Helvetica", 16), fill="#f9e4bc")
    levels=["Easy", "Medium", "Advanced"]
    y=150
    for level in levels:
        BTN=tk.Button(main_gui, text=level, width=20, font=("Helvetica", 12),
                          command=lambda d=level: modestart(topic, d))
        canvas.create_window(width_window / 2, y, window=BTN)
        y += 40

    button_back=tk.Button(main_gui, text="Back to levels", width=20, font=("Helvetica", 12),
                              command=lambda: modes_maths_show(player_name))
    canvas.create_window(width_window / 2, y + 20, window=button_back)

def show_instructions(): # When the user presses the instructions button.
    messagebox.showinfo("Instructions",
                            "Complete each math equations escape!\n"
                            "Each correct question will allow you to escape.\n"
                            "Be Cautious! Every mintue a new question will spawn.\n"
                            "\nHave fun and Answer Carefully!!!")

def game_exit():# When the user presses the Exit button this pops up.
    validate=messagebox.askyesno("Exit", "Do you really want leave the game?")
    if validate:
        main_gui.destroy()




class Mazegen_DFS:# Creating a auto generate maze algorithm.
    def __init__(code, rows, cols):
        code.rows=rows if rows % 2 !=0 else rows + 1
        code.cols=cols if cols % 2 !=0 else cols + 1
        code.grid=[[1 for _ in range(code.cols)] for _ in range(code.rows)]
        code.visited=[[False for _ in range(code.cols)] for _ in range(code.rows)]
        code.path_stack=[]

    def gen(code):
        row_start, col_start = random.randrange(1, code.rows, 2), random.randrange(1, code.cols, 2)
        code.grid[row_start][col_start]=0
        code.visited[row_start][col_start]=True
        code.path_stack.append((row_start, col_start))

        while code.path_stack:
            row_current, col_current = code.path_stack[-1]
            connecting=[]
            if row_current - 2 >= 0 and not code.visited[row_current - 2][col_current]:
                connecting.append((row_current - 2, col_current, row_current - 1, col_current))
            if row_current + 2 < code.rows and not code.visited[row_current + 2][col_current]:
                connecting.append((row_current + 2, col_current, row_current + 1, col_current))
            if col_current - 2 >= 0 and not code.visited[row_current][col_current - 2]:
                connecting.append((row_current, col_current - 2, row_current, col_current - 1))
            if col_current + 2 < code.cols and not code.visited[row_current][col_current + 2]:
                connecting.append((row_current, col_current + 2, row_current, col_current + 1))

            if connecting:
                row_next, col_next, row_wall, col_wall =random.choice(connecting)
                code.grid[row_wall][col_wall]=0
                code.grid[row_next][col_next]=0
                code.visited[row_next][col_next]=True
                code.path_stack.append((row_next, col_next))
            else:
                code.path_stack.pop()
        return code.grid
    def take_cells_path(code, grid_maze):
        cells_path=[]
        for r in range(code.rows):
            for c in range(code.cols):
                if grid_maze[r][c]==0:
                    cells_path.append((r, c))
        return cells_path
    def object_place_on_path(code, grid_maze, type_obj):
        cells_path=code.take_cells_path(grid_maze)
        path_cells_safe=[(r, c) for r, c in cells_path if (r, c) != (1,1) and (r, c) !=(code.rows - 2, code.cols - 2) and grid_maze[r][c]==0]
        if not path_cells_safe:
            return None, None
        r, c=random.choice(path_cells_safe)
        grid_maze[r][c]=type_obj
        return r, c

#math gen algorithm

def gen_math_equations(topic, level):# Creating a function to make new eqautions for different modes and topics.
    data_question={}

    if topic == "Calculus":# Checking if the user has picked the calcus topic.
        if level == "Easy":# Checking if the user has picked the easy mode.
            a = random.randint(2, 10)# Choosing a number between 2 and 10.
            n = random.choice([1, 2])# Chooses which question.
            if n == 1:# This is the first question.
                data_question['question'] = f"What is the derivative of {a}x?"# The question where as is the random number that has been chosen.
                data_question['answer'] = str(a)# Solves the awnser for {a}.
            else:
                data_question['question'] = f"What is the derivative of {a}x^2?"# The second question where {a} has a sqaure.
                data_question['answer'] = f"{2*a}x"# Awnser for The second question by using {a} to solve.
            data_question['type'] = 'text'# Entry field for the text.
        elif level == "Medium":# Checking if the user has picked the medium mode.
            a = random.randint(2, 10)# Choosing a number between 2 and 10.
            n = random.choice([0, 1])# Chooses which question.
            if n == 0:# If the question is question 0 then it displays the the first question.
                data_question['question'] = f"What is the indefinite integral of {a}? (include +C)"# The question where as is the random number that has been chosen.
                data_question['answer'] = f"{a}x + C"# Solves the awnser for {a} and adding +c.
            else:
                if a % 2 != 0: a += 1# If it randomly chooses question 1 and not 0 then the question pops up.
                data_question['question'] = f"What is the indefinite integral of {a}x? (include +C)"# The question where as is the random number that has been chosen.
                data_question['answer'] = f"{a//2}x^2 + C"# The second question where {a} has a sqaure with a +c at the end.
            data_question['type'] = 'text'# Entry field for the text.
        elif level == "Advanced":# If the user has choosen the addvanced mode.
            a1 = random.randint(2, 5)# Choosing a number between 2 and 5.
            a2 = random.randint(1, 4)# Choosing a number between 1 and 4.
            op = random.choice(['+', '-'])# Choosing a eqution bellow that has + or - .
            
            if op == '+': # If the question is plus and the 2 random number for a1 and a2 has been choosen it gives the questions.
                data_question['question'] = f"What is the derivative of {a1}x^2 + {a2}x?"# The made question that has a + in it.
                data_question['answer'] = f"{2*a1}x + {a2}"# Formula for sovling the question.
            else:
                data_question['question'] = f"What is the derivative of {a1}x^2 - {a2}x?"# The question that has a - in it.
                data_question['answer'] = f"{2*a1}x - {a2}"# Formula for solveing the question.
            data_question['type'] = 'text'# Entry field.



    if topic == "Algebra":# If the user picks the algebra topic.
        if level == "Easy":# If the user picks the easy mode.
            a = random.choice([1, random.randint(2, 3)])# Chooses 1 first then a random number between 2 and 3 then the random.choice chooses one from the two values.
            b = random.randint(1, 10) * random.choice([-1, 1])#Chooses a random number between 1 and 10 then a random choice between -1 and 1.
            x_val = random.randint(-5, 10)# Chooses a random number between -5 and 10 for a value.
            c = a * x_val + b# Question formula to solve for c using a b and x_val.
            data_question['question'] = f"What is X? {a}X {'+' if b >= 0 else ''} {b} = {c}"# The question the with the a and b and c varibles in the question.
            data_question['answer'] = str(x_val)# The string of x_val is the awsner and it solves the question and checks if correct then returns if right then right sound if wrong then a wrong sound will play.
            data_question['type'] = 'text'# Entry field.
        elif level == "Medium":# If the user has chosen the medium mode.
            a = random.randint(3, 8) * random.choice([-1, 1])# Random number is chosen. 
            c = random.randint(1, 4) * random.choice([-1, 1])# Random number is chosen.
            while a == c:# If c then do the following down.
                c = random.randint(1, 4) * random.choice([-1, 1])# Random number is picked.
            b = random.randint(-10, 10)
            d = random.randint(-10, 10)
            
            x_val_numerator = d - b
            x_val_denominator = a - c
            if x_val_denominator == 0:
                return gen_math_equations(topic, level)
            
            if x_val_numerator % x_val_denominator != 0:
                d += x_val_denominator - (x_val_numerator % x_val_denominator)
                if x_val_numerator % x_val_denominator < 0:
                    d += x_val_denominator
                
            x_val = (d - b) // (a - c)
            data_question['question'] = f"What is X? {a}X {'+' if b >= 0 else ''} {b} = {c}X {'+' if d >= 0 else ''} {d}"
            data_question['answer'] = str(x_val)
            data_question['type'] = 'text'
        elif level == "Advanced":
            a = random.randint(2, 5)
            b = random.randint(-5, 5)
            x_val = random.randint(-8, 8)
            c = a * (x_val + b)
            data_question['question'] = f"What is X? {a}(X {'+' if b >= 0 else ''} {b}) = {c}"
            data_question['answer'] = str(x_val)
            data_question['type'] = 'text'
    
    elif topic == "Geometry":
        if level == "Easy":
            global final_geo_point
            while True:
                x_val = random.randint(-5, 5)
                y_val = random.randint(-5, 5)
                if (x_val, y_val) != final_geo_point:
                    break
            last_geometry_point = (x_val, y_val)

            data_question['question'] = f"Identify the coordinates of the RED point."
            data_question['answer'] = f"({x_val},{y_val})"
            data_question['type'] = 'graph'
            data_question['point'] = (x_val, y_val)
            data_question['range_x'] = (-6, 6)
            data_question['range_y'] = (-6, 6)

        elif level == "Medium":
            length = random.randint(3, 10)
            width = random.randint(2, 8)
            data_question['question'] = f"A rectangle has a length of {length} units and a width of {width} units. What is its area? (units squared)"
            data_question['answer'] = str(length * width)
            data_question['type'] = 'text'

        elif level == "Advanced":
            side_a = random.randint(3, 6)
            side_b = random.randint(3, 6)
            hypotenuse_squared = side_a**2 + side_b**2
            if math.isqrt(hypotenuse_squared)**2 != hypotenuse_squared:
                return gen_math_equations(topic, level)

            hypotenuse = math.isqrt(hypotenuse_squared)
            data_question['question'] = f"A right-angled triangle has sides of {side_a} and {side_b}. What is the length of the hypotenuse?"
            data_question['answer'] = str(hypotenuse)
            data_question['type'] = 'text'
            
    elif topic == "Exponents":
        if level == "Easy":
            base = random.randint(2, 5)
            exp = random.randint(2, 4)
            data_question['question'] = f"What is {base}^{exp}?"
            data_question['answer'] = str(base ** exp)
            data_question['type'] = 'text'
        elif level == "Medium":
            base = random.randint(2, 5)
            exp1 = random.randint(1, 3)
            exp2 = random.randint(1, 3)
            data_question['question'] = f"Simplify: {base}^{exp1} * {base}^{exp2}"
            data_question['answer'] = f"{base}^{exp1 + exp2}"
            data_question['type'] = 'text'
        elif level == "Advanced":
            base = random.randint(2, 5)
            exp1 = random.randint(3, 6)
            exp2 = random.randint(1, exp1 - 1)
            data_question['question'] = f"Simplify: {base}^{exp1} / {base}^{exp2}"
            data_question['answer'] = f"{base}^{exp1 - exp2}"
            data_question['type'] = 'text'
    elif topic == "Fractions":
        if level == "Easy":
            den = random.randint(2, 10)
            num1 = random.randint(1, den - 1)
            num2 = random.randint(1, den - 1)
            op = random.choice(['+', '-'])
            
            if op == '+':
                result = Fraction(num1, den) + Fraction(num2, den)
            else:
                result = Fraction(num1, den) - Fraction(num2, den)
            
            data_question['question'] = f"What is {num1}/{den} {op} {num2}/{den}? (Simplify your answer, e.g., 1/2 or -3/4)"
            data_question['answer'] = str(result)
            data_question['type'] = 'text'
        elif level == "Medium":
            den1 = random.randint(2, 6)
            den2 = random.randint(2, 6)
            while den1 == den2:
                den2 = random.randint(2, 6)
            num1 = random.randint(1, den1 - 1)
            num2 = random.randint(1, den2 - 1)
            op = random.choice(['+', '-'])

            f1 = Fraction(num1, den1)
            f2 = Fraction(num2, den2)
            
            if op == '+':
                result = f1 + f2
            else:
                result = f1 - f2
            
            data_question['question'] = f"What is {num1}/{den1} {op} {num2}/{den2}? (Simplify your answer)"
            data_question['answer'] = str(result)
            data_question['type'] = 'text'
        elif level == "Advanced":
            den1 = random.randint(2, 8)
            den2 = random.randint(2, 8)
            num1 = random.randint(1, den1 + 2)
            num2 = random.randint(1, den2 + 2)
            op = random.choice(['*', '/'])

            f1 = Fraction(num1, den1)
            f2 = Fraction(num2, den2)
            
            if op == '*':
                result = f1 * f2
                data_question['question'] = f"What is {num1}/{den1} * {num2}/{den2}? (Simplify your answer)"
            else:
                if num2 == 0: return gen_math_equations(topic, level)
                result = f1 / f2
                data_question['question'] = f"What is {num1}/{den1} / {num2}/{den2}? (Simplify your answer)"
            
            data_question['answer'] = str(result)
            data_question['type'] = 'text'
    elif topic == "Number Theory":
        if level == "Easy":
            num = random.randint(12, 30)
            factors = [i for i in range(1, num + 1) if num % i == 0]
            data_question['question'] = f"List all positive factors of {num} (e.g., 1,2,3,4,6,12)"
            data_question['answer'] = ",".join(map(str, sorted(factors)))
            data_question['type'] = 'text'
        elif level == "Medium":
            num = random.randint(10, 50)
            is_prime = all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)) and num > 1
            data_question['question'] = f"Is {num} a prime or composite number?"
            data_question['answer'] = "prime" if is_prime else "composite"
            data_question['type'] = 'text'
        elif level == "Advanced":
            n1 = random.randint(5, 20)
            n2 = random.randint(5, 20)
            op = random.choice(['LCM', 'GCD'])
            if op == 'LCM':
                result = (n1 * n2) // math.gcd(n1, n2)
                data_question['question'] = f"What is the Lowest Common Multiple (LCM) of {n1} and {n2}?"
            else:
                result = math.gcd(n1, n2)
                data_question['question'] = f"What is the Greatest Common Divisor (GCD) of {n1} and {n2}?"
            data_question['answer'] = str(result)
            data_question['type'] = 'text'


    if not data_question:
        data_question['question'] = "This puzzle type is not yet implemented for this difficulty. What is 5 + 5?"
        data_question['answer'] = "10"
        data_question['type'] = 'text'

    return data_question

def draw_graph(canvas_graph, range_x, range_y, plot_to_point=None):# Create the maze so that the player can move around.
    canvas_graph.delete("all")
    width_graph = 400  
      

    padding = 40
    left_draw = padding
    top_draw = padding
    right_draw = width_graph - padding
    bottom_draw = width_graph - padding

    if right_draw <= left_draw or bottom_draw <= top_draw:
        return

    canvas_graph.create_line(left_draw, bottom_draw, right_draw, bottom_draw, fill="black", width=2, arrow=tk.LAST)
    canvas_graph.create_line(left_draw, bottom_draw, left_draw, top_draw, fill="black", width=2, arrow=tk.LAST)

    x_val_range = range_x[1] - range_x[0]
    y_val_range = range_y[1] - range_y[0]

    if x_val_range == 0: x_val_range = 1
    if y_val_range == 0: y_val_range = 1

    x_pixels_per_unit = (right_draw - left_draw) / x_val_range
    y_pixels_per_unit = (bottom_draw - top_draw) / y_val_range

    for x_val in range(range_x[0], range_x[1] + 1):
        x_pos = (x_val - range_x[0]) * x_pixels_per_unit + left_draw
        canvas_graph.create_line(x_pos, bottom_draw - 5, x_pos, bottom_draw, fill="black")
        if x_val != 0:
            canvas_graph.create_text(x_pos, bottom_draw + 15, text=str(x_val), font=("Arial", 8), anchor="n")
    
    for y_val in range(range_y[0], range_y[1] + 1):
        y_pos = bottom_draw - ((y_val - range_y[0]) * y_pixels_per_unit)
        canvas_graph.create_line(left_draw - 5, y_pos, left_draw, y_pos, fill="black")
        if y_val != 0:
            canvas_graph.create_text(left_draw - 12, y_pos, text=str(y_val), font=("Arial", 8), anchor="e")

    canvas_graph.create_text(left_draw - 10, bottom_draw + 10, text="0", font=("Arial", 8), anchor="ne")

    canvas_graph.create_text(right_draw + 20, bottom_draw, text="X", anchor="w", font=("Arial", 10, "bold"))
    canvas_graph.create_text(left_draw, top_draw - 20, text="Y", anchor="s", font=("Arial", 10, "bold"))

    if point_to_plot:
        px, py = point_to_plot
        
        canvas_x = (px - range_x[0]) * x_pixels_per_unit + left_draw
        canvas_y = bottom_draw - ((py - range_y[0]) * y_pixels_per_unit)

        radius = 5
        canvas_graph.create_oval(canvas_x - radius, canvas_y - radius,
                                  canvas_x + radius, canvas_y + radius,
                                  fill="red", outline="red")


def puzzle_trap(second_window, bg_maze, row_problem, col_problem, topic, level,
                grid_maze, player_name, completed_puzzel_track, total_problems, sketch_maze_function, UPD_user_total_progress_fuctions,
                on_game_start_callback, on_quiz_end_callback): # When the player lands on the puzzel it pops a equation.
    
    on_game_start_callback()

    game_window = tk.Toplevel(second_window)
    game_window.title(f"Solve the {topic} Equation!")
    game_window.geometry("500x400")
    game_window.transient(second_window) 
    game_window.grab_set() 
    
    second_x = second_window.winfo_x()
    second_y = second_window.winfo_y()
    second_width = second_window.winfo_width()
    second_height = second_window.winfo_height()

    game_window_width = 500
    game_window_height = 400

    center_x = second_x + second_width // 2 - game_window_width // 2
    center_y = second_y + second_height // 2 - game_window_height // 2
    game_window.geometry(f"+{center_x}+{center_y}")


    data_question = gen_math_equations(topic, level)
    question_text = data_question['question']
    correct_answer = data_question['answer']
    question_type = data_question['type']

    tk.Label(game_window, text=question_text, font=("Helvetica", 16), wraplength=480).pack(pady=10)

    graph_area = None
    if question_type == 'graph':
        graph_area = tk.Canvas(game_window, width=400, height=200, bg="white", highlightbackground="black", highlightthickness=1)
        graph_area.pack(pady=10)
        
        game_window.update()   
        draw_graph(graph_area, data_question['range_x'], data_question['range_y'], data_question['point'])

    answer_entry = tk.Entry(game_window, font=("Helvetica", 14), width=30)
    answer_entry.pack(pady=10)
    answer_entry.focus_set()# Made it so that if when the question pops up the player can awnser it without clicking on the window.
    if question_type == 'graph':
        tk.Label(game_window, text="Format: (X,Y) e.g., (3,-2). No spaces.", font=("Helvetica", 10, "italic")).pack()# Hints.
    elif topic == "Fractions":
        tk.Label(game_window, text="Format: numerator/denominator e.g., 3/4. For negative, -3/4. For integers, 5.", font=("Helvetica", 10, "italic")).pack()# Hints.
    elif topic == "Exponents" and level in ["Medium", "Advanced"]:
        tk.Label(game_window, text="Format: base^exponent e.g., 2^5", font=("Helvetica", 10, "italic")).pack()# Hints.
    elif topic == "Number Theory" and level == "Easy":
        tk.Label(game_window, text="Format: comma-separated list, ascending e.g., 1,2,3,4", font=("Helvetica", 10, "italic")).pack()# Hints.
    elif topic == "Calculus" and level in ["Medium", "Advanced"]:
        tk.Label(game_window, text="Format: expression with +C e.g., 3x^2 + 5x + C", font=("Helvetica", 10, "italic")).pack()# Hints.


    def on_submit_or_close():# Creating a function so that onces the player awnser the question it pops up and they can press ok.
        player_answer = answer_entry.get().strip()
        
        if question_type == 'graph':
            player_answer = coordinate_normalize_entry(player_answer)
        if player_answer == correct_answer:
            
            if sound_correct:
                try:
                    sound_correct.play()
                except Exception as e:
                    print("Error playing correct answer sound:", e)
            
            messagebox.showinfo("Correct!", "You solved the equation! The path is now clear.")
            grid_maze[row_problem][col_problem] = 0 
            completed_puzzel_track[0] += 1  
            sketch_maze_function()
            on_quiz_end_callback()
            game_window.destroy()
            
            return
            
        if sound_wrong:
            try:
                sound_wrong.play()
            except Exception as e:
                print("Error playing wrong answer sound:", e)
            
        messagebox.showerror("Incorrect!", "That's not right. Keep trying!")
        on_quiz_end_callback()
        game_window.destroy()# Closes the window if the player gets it wrong.
 


    submit_button = tk.Button(game_window, text="Submit Answer", font=("Helvetica", 12), command=on_submit_or_close)
    submit_button.pack(pady=10)
    game_window.bind('<Return>', lambda event:on_submit_or_close())

    def close_submit():
        if messagebox.askyesno("Quit", "Are you sure you really want to not answer the question"):
            on_quiz_end_callback()
            game_window.destroy()

    game_window.protocol("WM_DELETE_WINDOW", close_submit) 

class MazeWindow:
    def __init__(code, ms, grid_maze, player_name, maze_number_rows, maze_number_cols, original_puzzels,
                 math_topic, level, main_menu_reset_function, UPD_user_total_progress_fuctions): # Creating a new maze window in my game.

        code.ms = ms 
        code.maze_gui = tk.Toplevel(ms) 
        code.maze_gui.title(f"{player_name}'s {level} {math_topic} Maze Escape!")
        code.maze_gui.protocol("WM_DELETE_WINDOW", code.on_close) 

        code.grid_maze = grid_maze
        code.player_name = player_name
        code.maze_number_rows = maze_number_rows
        code.maze_number_cols= maze_number_cols
        code.original_puzzels = original_puzzels 
        code.math_topic = math_topic
        code.level = level
        code.main_menu_reset_function = main_menu_reset_function
        code.UPD_user_total_progress_fuctions = UPD_user_total_progress_fuctions
        code.minimum_cube_size = 10
        code.new_puzzle_timer_id = None
        code.HEADER_HEIGHT_ADVANCED = 80  
        code.HEADER_HEIGHT_EASY = 60 
        code.FOOTER_HEIGHT = 60  

        code.MAZE_PADDING = 20 
        
        code.is_easy_mode = (code.level == "Easy")

        
        code.start_time = time.time()
        code.elapsed_time = 0  

        
        if code.level == "Advanced":
            original_window_width = 700 
            original_window_height = 700
        else: 
            original_window_width = code.maze_number_cols * 30 + (code.MAZE_PADDING * 2) 
            original_window_height = code.maze_number_rows * 30 + (code.MAZE_PADDING * 2) 
            if not code.is_easy_mode:
                original_window_height += code.HEADER_HEIGHT_ADVANCED + code.FOOTER_HEIGHT
            else:
                original_window_height += code.HEADER_HEIGHT_EASY + code.FOOTER_HEIGHT 

        
        if original_window_width < 500: original_window_width = 500
        if original_window_height < 500: original_window_height = 500
        
        code.maze_gui.geometry(f"{original_window_width}x{original_window_height}")
        code.maze_gui.resizable(True, True) 

        
        screen_width = code.maze_gui.winfo_screenwidth()
        screen_height = code.maze_gui.winfo_screenheight()

        center_x = screen_width // 2 - original_window_width // 2
        center_y = screen_height // 2 - original_window_height // 2
        code.maze_gui.geometry(f"+{center_x}+{center_y}")


        code.canvas = tk.Canvas(code.maze_gui, bg="#333333")
        code.canvas.pack(fill="both", expand=True)

        
        try:
            img = Image.open(get_image_location("resized_image.png"))
            
            code.bg_original_image = img 
            code.bg_image_tk = None 
        except FileNotFoundError:
            messagebox.showerror("Image Error", f"Maze background image not found: {get_image_location('resized_image.png')}")
            code.canvas.config(bg="#B0C4DE") 
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading maze background image: {e}")
            code.canvas.config(bg="#B0C4DE") 

        code.user_pos_x, code.user_pos_y = 1, 1 
        code.user_canvas_id = None
        
        
        code.maze_leave_x, code.maze_leave_y = code.maze_number_cols - 2, code.maze_number_rows - 2
        code.grid_maze[code.maze_leave_y][code.maze_leave_x] = 'E' 

        code.completed_puzzel_track = [0] 
        code.is_quiz_online_flag = False 
        code.working_puzzles = {} 

        
        code.total_present_puzzles = original_puzzels 

        
        code.place_original_puzzles(original_puzzels)

        
        code.exit_button = tk.Button(code.maze_gui, text="Exit Maze to Main Menu",
                                     font=("Helvetica", 10), command=code.confirm_leaving_maze)
        code.exit_button_id = None 

        code.sketch_maze_function() 
        code.update_timer() 

        code.bind_movement_keys()

        
        code.canvas.bind("<Configure>", code.on_canvas_resize)

        
        code.new_puzzle_timer_id = code.maze_gui.after(60000, code.add_new_puzzle_periodically)

        
        code.new_puzzle_label_id = None


    def place_original_puzzles(code, count):# This function is for user to solve the puzzels that where on the maze when the game just started.
        maze_gen = Mazegen_DFS(code.maze_number_rows, code.maze_number_cols) 
        for _ in range(count):
            r, c = maze_gen.object_place_on_path(code.grid_maze, 'Q')
            if r is not None and c is not None:
                code.working_puzzles[(r, c)] = True

    def add_new_puzzle_periodically(code):# Adding new questions randomly in game in each mode and also displays for 1 minute so that the player knows.
        
        if not code.is_quiz_online_flag:
            maze_gen = Mazegen_DFS(code.maze_number_rows, code.maze_number_cols)
            r, c = maze_gen.object_place_on_path(code.grid_maze, 'Q')
            if r is not None and c is not None:
                code.working_puzzles[(r, c)] = True
                code.total_present_puzzles += 1 
                code.sketch_maze_function() 
                
                
                current_canvas_width = code.canvas.winfo_width()
                current_canvas_height = code.canvas.winfo_height()
                
                if code.new_puzzle_label_id:
                    code.canvas.delete(code.new_puzzle_label_id) 

                
                if code.is_easy_mode:
                    notification_y = code.HEADER_HEIGHT_EASY + code.MAZE_PADDING / 2
                else:
                    notification_y = code.HEADER_HEIGHT_ADVANCED - 20 

                code.new_puzzle_label_id = code.canvas.create_text(
                    current_canvas_width / 2, notification_y, 
                    text="A new equation has spawned in the maze!",
                    font=("Helvetica", 16, "bold"),
                    fill="yellow",
                    tags="new_puzzle_notification"
                )
                code.canvas.tag_raise("new_puzzle_notification")
                
                
                code.maze_gui.after(3000, lambda: code.canvas.delete(code.new_puzzle_label_id))
        
        
        if code.maze_gui.winfo_exists():
            code.new_puzzle_timer_id = code.maze_gui.after(60000, code.add_new_puzzle_periodically)


    def on_canvas_resize(code, event=None):# Changes the maze when ever the canvas dimensions changes.
        code.sketch_maze_function()

    def sketch_maze_function(code):# To redraw maze, ui and the player every game and every time.
        code.canvas.delete("all") 
        
        current_canvas_width = code.canvas.winfo_width()
        current_canvas_height = code.canvas.winfo_height()

        
        if code.bg_original_image:
            img = code.bg_original_image.resize((current_canvas_width, current_canvas_height), Image.Resampling.LANCZOS)
            code.bg_image_tk = ImageTk.PhotoImage(img)
            code.canvas.create_image(0, 0, image=code.bg_image_tk, anchor="nw")

        
        usable_height = current_canvas_height - (code.MAZE_PADDING * 2)
        usable_width = current_canvas_width - (code.MAZE_PADDING * 2)

        header_height = code.HEADER_HEIGHT_EASY if code.is_easy_mode else code.HEADER_HEIGHT_ADVANCED
        usable_height -= (header_height + code.FOOTER_HEIGHT)

        
        if code.maze_number_cols > 0 and code.maze_number_rows > 0:
            potential_cell_size_w = usable_width / code.maze_number_cols
            potential_cell_size_h = usable_height / code.maze_number_rows
            code.cell_size = max(code.minimum_cube_size, min(potential_cell_size_w, potential_cell_size_h))
        else:
            code.cell_size = code.min_cell_size 

        
        maze_width = code.maze_number_cols * code.cell_size
        maze_height = code.maze_number_rows * code.cell_size
        
        
        offset_x = (current_canvas_width - maze_width) / 2
        offset_y = header_height + (usable_height - maze_height) / 2 + code.MAZE_PADDING #

        
        if offset_x < code.MAZE_PADDING: offset_x = code.MAZE_PADDING

        
        header_center_x = current_canvas_width / 2

        if code.is_easy_mode:
            
            title_y = code.MAZE_PADDING + 10 
            instructions_y = title_y + 25 

            code.canvas.create_text(header_center_x, title_y, text=f"{code.player_name}'s Maze Escape!", font=("Helvetica", 20, "bold"), fill="white", tags="ui_element")
            code.canvas.create_text(header_center_x, instructions_y, text="Use Arrow Keys to Move", font=("Helvetica", 14), fill="white", tags="ui_element")

            
            timer_y = offset_y + maze_height + 20  
            code.canvas.create_text(header_center_x, timer_y, text=f"Time: {code.format_elapsed_time(code.elapsed_time)}", font=("Helvetica", 14, "bold"), fill="yellow", tags="ui_element")

            
            if code.exit_button_id:
                code.canvas.delete(code.exit_button_id)
            code.exit_button_id = code.canvas.create_window(
                current_canvas_width / 2 - code.exit_button.winfo_reqwidth() / 2 - 20, 
                current_canvas_height - code.FOOTER_HEIGHT / 2, 
                window=code.exit_button, 
                tags="ui_element",
                anchor="center"
            )

            
            progress_text = f"Puzzles Solved: {code.completed_puzzel_track[0]} / {code.total_present_puzzles}"
            code.canvas.create_text(
                current_canvas_width / 2 + code.exit_button.winfo_reqwidth() / 2 + 20, 
                current_canvas_height - code.FOOTER_HEIGHT / 2, 
                text=progress_text, 
                font=("Helvetica", 14, "bold"), 
                fill="white", 
                tags="ui_element",
                anchor="center"
            )

        else: 
            title_y = code.HEADER_HEIGHT_ADVANCED / 4
            instructions_y = code.HEADER_HEIGHT_ADVANCED / 4 * 3

            code.canvas.create_text(header_center_x, title_y, text=f"{code.player_name}'s Maze Escape!", font=("Helvetica", 20, "bold"), fill="white", tags="ui_element")
            code.canvas.create_text(header_center_x, instructions_y, text="Use Arrow Keys to Move", font=("Helvetica", 14), fill="white", tags="ui_element")

            
            timer_text = f"Time: {code.format_elapsed_time(code.elapsed_time)}"
            code.canvas.create_text(code.MAZE_PADDING + 150, code.HEADER_HEIGHT_ADVANCED / 2, text=timer_text, font=("Helvetica", 14, "bold"), fill="yellow", anchor="center", tags="ui_element")
            
            
            progress_text = f"Puzzles Solved: {code.completed_puzzel_track[0]} / {code.total_present_puzzles}"
            code.canvas.create_text(current_canvas_width - code.MAZE_PADDING, instructions_y, text=progress_text, font=("Helvetica", 14, "bold"), fill="white", anchor="e", tags="ui_element")

            
            if code.exit_button_id:
                code.canvas.delete(code.exit_button_id) 
            code.exit_button_id = code.canvas.create_window(
                code.MAZE_PADDING + code.exit_button.winfo_reqwidth() / 2 + 10,
                code.HEADER_HEIGHT_ADVANCED / 2, 
                window=code.exit_button, 
                tags="ui_element",
                anchor="center"
            )


        
        for r in range(code.maze_number_rows):
            for c in range(code.maze_number_cols):
                x1 = c * code.cell_size + offset_x
                y1 = r * code.cell_size + offset_y
                x2 = x1 + code.cell_size
                y2 = y1 + code.cell_size

                cell_type = code.grid_maze[r][c]

                if cell_type == 1: 
                    code.canvas.create_rectangle(x1, y1, x2, y2, fill="#4A4A4A", outline="#333333")
                elif cell_type == 0: 
                    code.canvas.create_rectangle(x1, y1, x2, y2, fill="#B0C4DE", outline="")
                elif cell_type == 'E': 
                    code.canvas.create_oval(x1 + code.cell_size*0.15, y1 + code.cell_size*0.15, x2 - code.cell_size*0.15, y2 - code.cell_size*0.15, fill="green", tags="exit")
                elif cell_type == 'Q': 
                    code.canvas.create_rectangle(x1 + code.cell_size*0.25, y1 + code.cell_size*0.25, x2 - code.cell_size*0.25, y2 - code.cell_size*0.25, fill="orange", outline="darkorange", width=1, tags="puzzle_object")

        
        player_inner_pad_ratio = 0.15 
        player_x1 = code.user_pos_x * code.cell_size + code.cell_size * player_inner_pad_ratio + offset_x
        player_y1 = code.user_pos_y * code.cell_size + code.cell_size * player_inner_pad_ratio + offset_y
        player_x2 = (code.user_pos_x + 1) * code.cell_size - code.cell_size * player_inner_pad_ratio + offset_x
        player_y2 = (code.user_pos_y + 1) * code.cell_size - code.cell_size * player_inner_pad_ratio + offset_y
        

        code.user_canvas_id = code.canvas.create_rectangle(player_x1, player_y1, player_x2, player_y2, fill="red", outline="", width=3, tags="player")


        code.canvas.tag_raise("player") 
        code.canvas.tag_raise("ui_element") 


    def format_elapsed_time(code, seconds):# To display the time on the gui.
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        return f"{minutes:02d}:{sec:02d}"

    def update_timer(code):# Making sure to keep track of how long the user has been in the game.
        if not code.is_quiz_online_flag:
            code.elapsed_time = time.time() - code.start_time
            
            code.sketch_maze_function()
        
        if code.maze_gui.winfo_exists():
            code.maze_gui.after(1000, code.update_timer)

    def set_quiz_active_status(code, is_active): # To keep track if the puzzel window is still open.
        code.is_quiz_online_flag = is_active
        if not is_active and code.maze_gui.winfo_exists():
            code.maze_gui.focus_set()

    def move_player(code, dx, dy):# To move the player and checking if they have completed all puzzles or not.
        if code.is_quiz_online_flag: 
            return

        new_x, new_y = code.user_pos_x + dx, code.user_pos_y + dy

        
        if not (0 <= new_y < code.maze_number_rows and 0 <= new_x < code.maze_number_cols):
            return

        
        if code.grid_maze[new_y][new_x] == 1: 
            return

        
        code.user_pos_x, code.user_pos_y = new_x, new_y
        code.update_player_position_on_canvas()

       
        if code.grid_maze[new_y][new_x] == 'E': 
            if code.completed_puzzel_track[0] >= code.total_present_puzzles:
                
                total_time_taken = time.time() - code.start_time
                messagebox.showinfo("Congratulations!", f"Well done, {code.player_name}! You solved all puzzles and escaped the maze!\nTime taken: {code.format_elapsed_time(total_time_taken)}")
                
                code.UPD_user_total_progress_fuctions(code.player_name, added_puzzels=code.completed_puzzel_track[0], added_mazes=1, taken_time=total_time_taken) 
                code.on_close() 
            else:
                messagebox.showwarning("Exit Blocked!", f"You need to solve all {code.total_present_puzzles} equations to escape! You have solved {code.completed_puzzel_track[0]}.")
            return
        elif code.grid_maze[new_y][new_x] == 'Q': 
            
            puzzle_trap(code.maze_gui, code.canvas, new_y, new_x, 
                           code.math_topic, code.level, code.grid_maze, 
                           code.player_name, code.completed_puzzel_track, 
                           code.total_present_puzzles, 
                           code.sketch_maze_function, 
                           code.UPD_user_total_progress_fuctions,
                           lambda: code.set_quiz_active_status(True), # Callback for quiz start.
                           lambda: code.set_quiz_active_status(False))


    def update_player_position_on_canvas(code):#It updates the current positon of the player and displays it on the console.
        current_canvas_width = code.canvas.winfo_width()
        current_canvas_height = code.canvas.winfo_height()

        maze_width = code.maze_number_cols * code.cell_size
        maze_height = code.maze_number_rows * code.cell_size
        
        
        header_height = code.HEADER_HEIGHT_EASY if code.is_easy_mode else code.HEADER_HEIGHT_ADVANCED
        usable_height_for_maze = current_canvas_height - (code.MAZE_PADDING * 2) - (header_height + code.FOOTER_HEIGHT)

        
        offset_x = (current_canvas_width - maze_width) / 2
        offset_y = header_height + (usable_height_for_maze - maze_height) / 2 + code.MAZE_PADDING 
        
        
        if offset_x < code.MAZE_PADDING: offset_x = code.MAZE_PADDING

        player_inner_pad_ratio = 0.15 

        code.canvas.coords(code.user_canvas_id,
                        code.user_pos_x * code.cell_size + code.cell_size * player_inner_pad_ratio + offset_x,
                        code.user_pos_y * code.cell_size + code.cell_size * player_inner_pad_ratio + offset_y,
                        (code.user_pos_x + 1) * code.cell_size - code.cell_size * player_inner_pad_ratio + offset_x,
                        (code.user_pos_y + 1) * code.cell_size - code.cell_size * player_inner_pad_ratio + offset_y)
        code.canvas.tag_raise(code.user_canvas_id) 

    def bind_movement_keys(code):# Binding the red sqaure to the arrow keys on the keyboard.
        
        code.maze_gui.bind("<Up>", lambda e: code.move_player(0, -1))
        code.maze_gui.bind("<Down>", lambda e: code.move_player(0, 1))
        code.maze_gui.bind("<Left>", lambda e: code.move_player(-1, 0))
        code.maze_gui.bind("<Right>", lambda e: code.move_player(1, 0))
        
        code.maze_gui.focus_set()

    def confirm_leaving_maze(code):# If the user wants to leave the game mid way.
        if code.is_quiz_online_flag:
            messagebox.showwarning("Quiz Active", "Please close the quiz window first!")
            return

        confirm = messagebox.askyesno("Exit Maze", "Are you sure you want to exit to the Main Menu? Your current maze progress will be lost.")
        if confirm:
            code.on_close() 

    def on_close(code):# Closes the maze down and stops puzzels spawning in, also disable any user controls.
        
        if code.is_quiz_online_flag:
            messagebox.showwarning("Quiz Active", "Please close the quiz window first!")
            return
        
        
        if code.new_puzzle_timer_id:
            code.maze_gui.after_cancel(code.new_puzzle_timer_id)
            code.new_puzzle_timer_id = None

        
        code.maze_gui.unbind("<Up>")
        code.maze_gui.unbind("<Down>")
        code.maze_gui.unbind("<Left>")
        code.maze_gui.unbind("<Right>")
        code.maze_gui.destroy() 
        code.main_menu_reset_function()


def save_to_PDF():# Creating a function to save the progress to a pdf so the user can view it. 
    progress_load()
    path_file=filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save User data as PDF")
    if not path_file:
        return # If the user does changes their mind about saving the data.
    try:
        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt="LC - User Data", ln=True, align='c')
        pdf.ln(10)

        
        pdf.set_font("Arial", "B", 16)# Creating the table heading.
        pdf.cell(60, 10, "Name", 1)
        pdf.cell(40, 10, "Puzzels", 1)
        pdf.cell(40, 10, "Mazes", 1)
        pdf.cell(40, 10, "Fastest Time", 1)
        pdf.ln()

        pdf.set_font("Arial", size=12)# Setting the table content.
        for name, stats in player_statistics.items():
            Quick=stats.get('Fastest_time')
            if Quick is None:# If the player has not completed the maze.
                Str_time="N/A"
            else:
                minutes=int(Quick // 60)
                seconds=int(Quick % 60)
                Str_time=f"{minutes:02d}:{seconds:02d}"
            pdf.cell(60, 10, name, 1)
            pdf.cell(40, 10, str(stats.get('puzzles_completed',0)),1)
            pdf.cell(40, 10, str(stats.get('mazes_done',0)),1)
            pdf.cell(40, 10, Str_time,1)
            pdf.ln()
        pdf.output(path_file)
        messagebox.showinfo("Success", f"User Data saved as a PDF:\n{path_file}")
    except Exception as e:
        messagebox.showerror("Error", f"User Data can not be saved as a PDF:\n{e}")

def erase_all_progress():# Creating a funtion to remove all the progress if the user wants to.
    global player_statistics
    confirm=messagebox.askyesno("Erase Progress", "Do you really want to delete the progress histroy")
    if confirm:
        try:
            if os.path.exists(progress_txt_file):
                with open(progress_txt_file, 'w') as f:
                    f.write("")# To remove everything in the file.
            player_statistics={}
            messagebox.showinfo("Success", "History of progress has been erased.")
        except Exception as e:
            messagebox.showerror("Error", "Unable to erase progress history.")
            
def progress_show(): # Creating a gui when the player clicks the progress button that includes the erasing the history and saving to a pdf.
    progress_load() 

    progress_gui = tk.Toplevel(main_gui)
    progress_gui.title("Player Progress")
    progress_gui.geometry("500x500")
    progress_gui.transient(main_gui)
    progress_gui.grab_set()

    
    main_gui_x = main_gui.winfo_x()
    main_gui_y = main_gui.winfo_y()
    main_gui_width = main_gui.winfo_width()
    main_gui_height = main_gui.winfo_height()

    pw_width = 450
    pw_height = 350
    center_x = main_gui_x + main_gui_width // 2 - pw_width // 2
    center_y = main_gui_y + main_gui_height // 2 - pw_height // 2
    progress_gui.geometry(f"+{center_x}+{center_y}")

    
    progress_gui.configure(bg="#1E1E2F")

    title_label = tk.Label(progress_gui, text="Your Global Progress:", font=("Helvetica", 18, "bold"),
                            fg="#FFFFFF", bg="#1E1E2F")
    title_label.pack(pady=(15, 10))

    
    container = tk.Frame(progress_gui, bg="#1E1E2F")
    container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    canvas_container = tk.Canvas(container, bg="#1E1E2F", highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas_container.yview)
    scrollable_frame = tk.Frame(canvas_container, bg="#1E1E2F")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_container.configure(
            scrollregion=canvas_container.bbox("all")
        )
    )

    canvas_container.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_container.configure(yscrollcommand=scrollbar.set)

    canvas_container.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if not player_statistics:
        no_data_label = tk.Label(scrollable_frame, text="No progress data found. Play a maze to start tracking!",
                                 font=("Helvetica", 13), fg="#AAAAAA", bg="#1E1E2F", wraplength=400, justify="center")
        no_data_label.pack(pady=30)
    else:
        for name, stats in player_statistics.items():
            best_time_sec = stats.get('Fastest_time')
            if best_time_sec is None:
                best_time_display = "N/A"
            else:
                minutes = int(best_time_sec // 60)
                seconds = int(best_time_sec % 60)
                best_time_display = f"{minutes:02d}:{seconds:02d}"

            
            player_frame = tk.Frame(scrollable_frame, bg="#2A2A3D", bd=2, relief="ridge")
            player_frame.pack(fill="x", pady=8, padx=5)

            
            name_label = tk.Label(player_frame, text=name, font=("Helvetica", 15, "bold"),
                                  bg="#2A2A3D", fg="#FFD700")
            name_label.pack(anchor="w", padx=10, pady=(8, 2))

            
            details_text = (f"\u2605 Puzzles Solved: {stats['puzzles_completed']}\n"# Added a Unicode for special characters this code is for a star like a emoji.
                            f"\u26AA Mazes Completed: {stats['mazes_done']}\n"# Added a Unicode for special characters this code is for a white circle like a emoji.
                            f"\u23F1 Fastest Escape Time: {best_time_display}")# Added a Unicode for special characters this code is for a stop watch like a emoji.
            details_label = tk.Label(player_frame, text=details_text, font=("Helvetica", 13),
                                     bg="#2A2A3D", fg="#FFFFFF", justify="left")
            details_label.pack(anchor="w", padx=20, pady=(0, 8))

    pdf_button_save=tk.Button(progress_gui, text="Save As PDF", command=save_to_PDF, bg="#6272a4", fg="white", font=("Helvetica", 12, "bold"), relief="flat", padx=12, pady=6,
                             activebackground="#50fa7b", activeforeground="black", cursor="hand2")
    pdf_button_save.pack(pady=(0,10))

    button_delete=tk.Button(progress_gui, text="Erase Progress", command=lambda: [erase_all_progress(),progress_gui.destroy(), progress_show()],
                             bg="#ff5555", fg="white", font=("Helvetica", 12, "bold"), relief="flat", padx=12, pady=6,
                             activebackground="#ff4444", activeforeground="white", cursor="hand2")
    button_delete.pack(pady=(0,10))

    close_button = tk.Button(progress_gui, text="Close", command=progress_gui.destroy,
                             bg="#44475a", fg="white", font=("Helvetica", 12, "bold"), relief="flat", padx=12, pady=6,
                             activebackground="#6272a4", activeforeground="white", cursor="hand2")
    close_button.pack(pady=(0, 15))


def modestart(topic, level):# Creating a new maze at the mode that the user has chosen and genrating puzzels and converting the main menu to a the game window.
    global player_name # Taking and using the name stored in the global varible.

    
    main_gui.withdraw() 

    
    if level == "Easy":
        base_dim = 11 
        original_puzzles = 3 
    elif level == "Medium":
        base_dim = 21 
        original_puzzles = 3
    else: 
        base_dim = 31 
        original_puzzles = 5

    maze_number_rows = base_dim
    maze_number_cols = base_dim
    
    maze_gen = Mazegen_DFS(maze_number_rows, maze_number_cols)
    generated_maze_grid = maze_gen.gen()
    

    
    
    main_gui.maze_game_window = MazeWindow(
        main_gui, # Pass main_window as master.
        generated_maze_grid, # Pass the initially generated grid without puzzles.
        player_name, 
        maze_number_rows, 
        maze_number_cols, 
        original_puzzles, # Pass initial puzzle count.
        topic, 
        level, 
        lambda: main_gui.deiconify() or reset_main_gui(), # On close, show main window and reset menu.
        autoupdate_player_progress_overall # Pass the function reference.
    )



main_gui=tk.Tk()
main_gui.title("The Equation Maze Room")
main_gui.resizable(False, False)
progress_load()
bg_setup()
main_gui_setup()
main_gui.mainloop()
