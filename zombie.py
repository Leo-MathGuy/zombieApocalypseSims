"""Simple zombie simulation, read README for details
"""

# IMPORTS
import os
import random
import numpy as np
import tkinter
from time import sleep

# FILE
try:
    os.makedirs(os.path.dirname(__file__) + "/saves/")
except FileExistsError:
    pass


# CONSTANTS
PEOPLE = 50

WIDTH = 100
HEIGHT = 100

CWIDTH = 2000
CHEIGHT = 1400

CHANCE_TO_TRANSFER_VIRUS = 0.1
CHANCE_TO_DIE_OF_VIRUS = 0.08
CHANCE_TO_EXCHANGE_LIN = 0.15
CHANCE_TO_PLANE = 0.001

IMMUNITY_PER_DAY_MIN = 0
IMMUNITY_PER_DAY_MAX = 0.015

SAVE = os.path.dirname(__file__) + "/saves/save1.json"

DAYS = 1000


# Create thing
root = tkinter.Tk("Zombie Simulation")
c = tkinter.Canvas(root, bg="white", width=CWIDTH, height=CHEIGHT)


# District
class District:
    """A district for the zombie simulation"""

    def __init__(
        self,
        ppl: int,
        ctt: float,
        ctd: float,
        cte: float,
        ctp: float,
        ipdmin: float,
        ipdmax: float,
        x_pos: int,
        y_pos: int,
    ):
        """Create a district for the zombie simulation

        Args:
            ppl (int): People in district
            ctt (float): Chance to infect other person
            ctd (float): Chance for infected to die
            cte (float): Chance for exchange with other district
            ctp (float): Chance for plane
            ipdmin (float): Minimum immumity add per day
            ipdmax (float): Maximum immunity add per day
            x_pos (int): X posision in city
            y_pos (int): Y position in city
        """
        self.people = ppl
        self.infected = 0
        self.chance_to_die = ctd
        self.chance_to_transfer = ctt
        self.chance_to_exchange = cte
        self.chance_to_plane = ctp
        self.min_immunity_add = ipdmin
        self.max_immunity_add = ipdmax
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.immunity = 0

    def infect_locally(self) -> None:
        """Infects locally"""
        total_infected = self.infected
        chance_to_infect = self.chance_to_transfer
        immunity = self.immunity
        immunity = 1 - immunity
        chance_to_infect *= immunity
        newly_infected = 0
        for person in range(0, total_infected):
            if random.random() < chance_to_infect:
                newly_infected += 1
                new_person = person  # For vscode to shut up
                person = new_person

        total_infected += newly_infected
        self.infected = total_infected
        if self.infected > self.people:
            self.infected = self.people
        
        update_district_color(self.x_pos, self.y_pos)

    def infect_random_person(self) -> None:
        """Infect a random person"""
        if self.infected < self.people:
            self.infected += 1


# Create districts
class City:
    """A city for the zombie simulation"""

    def __init__(self, width: int, height: int, prints: bool):
        """Create a city

        Args:
            width (int): Width of city in districts
            height (int): Height of city in districts
            prints (bool): Whether to print progress
        """
        self.total_districts = height * width
        self.city = []
        self.width = width
        self.height = height
        self.stats = {}

        for i in range(0, width):
            temp = []
            for j in range(0, height):
                temp.append(
                    District(
                        PEOPLE,
                        CHANCE_TO_TRANSFER_VIRUS,
                        CHANCE_TO_DIE_OF_VIRUS,
                        CHANCE_TO_EXCHANGE_LIN,
                        CHANCE_TO_PLANE,
                        IMMUNITY_PER_DAY_MIN,
                        IMMUNITY_PER_DAY_MAX,
                        i,
                        j,
                    )
                )

                if prints:
                    completed = i * height + j + 1
                    total = self.total_districts
                    percent_rounded = round(completed / total * 100, 2)
                    print(
                        f"\r[{percent_rounded}%] {completed}/{total} Districts comleted",
                        end="",
                    )
            self.city.append(temp)
        if prints:
            print()

    def close_districts_coords(self, x_pos: int, y_pos: int) -> list[list[int, int]]:
        """Returns coords of up, left, right, and down districts

        Args:
            x_pos (int): X position of district
            y_pos (int): Y position of district

        Returns:
            list[list[int,int]]: Left, up, right, down of center district
        """
        left_dist = [x_pos - 1, y_pos]
        up_dist = [x_pos, y_pos - 1]
        right_dist = [x_pos + 1, y_pos]
        down_dist = [x_pos, y_pos + 1]

        if left_dist[0] < 0:
            left_dist = None
        if up_dist[1] < 0:
            up_dist = None
        if right_dist[0] >= self.width:
            right_dist = None
        if down_dist[1] >= self.height:
            down_dist = None

        return [left_dist, up_dist, right_dist, down_dist]

    def close_districts(self, center: District) -> list[District]:
        """Close districts, takes district as input and returns districts

        Args:
            center (District): Center district

        Returns:
            list[District]: List up left, up, right, and down districts, in order
        """
        x_pos = center.x_pos
        y_pos = center.y_pos

        left_dist = [x_pos - 1, y_pos]
        up_dist = [x_pos, y_pos - 1]
        right_dist = [x_pos + 1, y_pos]
        down_dist = [x_pos, y_pos + 1]

        if left_dist[0] < 0:
            left_dist = None
        if up_dist[1] < 0:
            up_dist = None
        if right_dist[0] >= self.width:
            right_dist = None
        if down_dist[1] >= self.height:
            down_dist = None

        if left_dist:
            left_dist = self.city[left_dist[0]][left_dist[1]]
        if up_dist:
            up_dist = self.city[up_dist[0]][up_dist[1]]
        if right_dist:
            right_dist = self.city[right_dist[0]][right_dist[1]]
        if down_dist:
            down_dist = self.city[down_dist[0]][down_dist[1]]

        return [left_dist, up_dist, right_dist, down_dist]

    def district_at_coords(self, x_pos: int, y_pos: int) -> District:
        """Return district at y, x

        Args:
            x_pos (int): X position
            y_pos (int): Y position

        Returns:
            District: The district at (x,y)
        """
        return self.city[x_pos][y_pos]

    def generate_stats(self) -> None:
        """Generate stats"""
        infected_list = []
        alive_list = []

        for column in self.city:
            for district in column:
                infected_list.append(district.infected)
                alive_list.append(district.people)

        self.stats["infected"] = infected_list
        self.stats["alive"] = alive_list
        self.stats["infected_mean"] = np.mean(infected_list)
        self.stats["alive_mean"] = np.mean(infected_list)

    def do_local_infects(self, prints: bool = False):
        """Do local infections in all districts

        Args:
            prints (bool, optional): Whether to print progress. Defaults to False.
        """
        for i in range(0, self.width):
            for j in range(0, self.height):
                self.city[i][j].infect_locally()
                if prints:
                    completed = i * self.height + j + 1
                    total = self.total_districts
                    percent_rounded = round(completed / total * 100, 4)
                    print(
                        f"\r[{percent_rounded}%] {completed}/{total} Districts comleted",
                        end="",
                    )

    def infect_random_person(self) -> None:
        """Infect a random person in a random district"""
        coords = self.get_random_coords()
        self.city[coords[0]][coords[1]].infect_random_person()
        update_district_color(*coords)

    def get_random_coords(self) -> tuple[int, int]:
        """Get random coords

        Returns:
            tuple[int,int]: (x, y) coords
        """
        x_pos = random.randint(0, self.width - 1)
        y_pos = random.randint(0, self.height - 1)
        return (x_pos, y_pos)

    def do_close_infect(self, x_pos: int, y_pos: int) -> None:
        """Close infect a district

        Args:
            x_pos (int): X position
            y_pos (int): Y position
        """
        close_districts = self.close_districts_coords(x_pos, y_pos)
        district = self.district_at_coords(x_pos, y_pos)

        for dsct in range(0, len(close_districts)):
            if not close_districts[dsct]:
                continue

            out_dsct = self.city[close_districts[dsct][0]][close_districts[dsct][1]]

            for infected in range(0, district.infected):
                if district.chance_to_exchange > random.random():
                    exchg_out = True
                    exchg_in = random.random() < (out_dsct.infected / out_dsct.people)

                    if exchg_in == exchg_out:
                        return

                    if exchg_in:
                        self.city[x_pos][y_pos].infected += 1
                        self.city[close_districts[dsct][0]][
                            close_districts[dsct][1]
                        ].infected -= 1
                        update_district_color(x_pos, y_pos)
                        update_district_color(close_districts[dsct][0], close_districts[dsct][1])

                    if exchg_out:
                        self.city[x_pos][y_pos].infected -= 1
                        self.city[close_districts[dsct][0]][
                            close_districts[dsct][1]
                        ].infected += 1
                        update_district_color(x_pos, y_pos)
                        update_district_color(close_districts[dsct][0], close_districts[dsct][1])

    def do_close_infects(self) -> None:
        """Close infect whole city"""
        for x_pos in range(0, self.width):
            for y_pos in range(0, self.height):
                self.do_close_infect(x_pos, y_pos)

    def is_fully_infected(self) -> bool:
        """Is the city fully infected?

        Returns:
            bool: Yes/no
        """
        fully_infected = True
        for x_pos in range(0, self.width):
            for y_pos in range(0, self.height):
                if self.city[x_pos][y_pos].infected != self.city[x_pos][y_pos].people:
                    fully_infected = False

        return fully_infected


# Test city
print("Creating city...")
test = City(WIDTH, HEIGHT, False)

deeta = []

# Canvas things
c.pack()
c_districts = []
c_district_texts = []
district_width = CWIDTH / WIDTH
district_height = (CHEIGHT - 100) / HEIGHT


# Colors rgb to hex
def rgb_to_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    return "#%02x%02x%02x" % rgb


# Percent to color
def percent_to_color(percent: float) -> str:
    """Green -> Yellow -> Red map

    Args:
        percent (float): Percent

    Returns:
        str: Hex
    """
    # print("\n", percent)
    # print(percent)
    pct_diff = 1.0 - percent
    red_color = min(255, pct_diff * 2 * 255)
    green_color = min(255, percent * 2 * 255)
    colors = (round(red_color), round(green_color), 0)
    return rgb_to_hex(colors)


# Create canvas districts
for i in range(0, WIDTH):
    c_districts.append(list())
    c_district_texts.append(list())
    for j in range(0, HEIGHT):
        c_districts[i].append(
            c.create_rectangle(
                i * district_width,
                j * district_height,
                (i + 1) * district_width,
                (j + 1) * district_height,
                outline="black",
                width=1,
                fill=percent_to_color(0),
            )
        )
        c_district_texts[i].append(
            c.create_text(
                i * district_width + district_width/2,
                j * district_height + district_height/2,
                text="",
                font=("Roboto", 4)
            )
        )


# Update district color
def update_district_color(x: int, y: int) -> None:
    """Update district's color

    Args:
        x (int): x position
        y (int): y position
    """
    district = test.district_at_coords(x, y)
    infectedpercent = 1 - (district.infected / district.people)

    if infectedpercent < 1:
        c.itemconfig(c_districts[x][y], {"width": 2})
        c.itemconfig(c_district_texts[x][y], {"text": str(district.infected)+"/"+str(district.people)})
    else:
        c.itemconfig(c_districts[x][y], {"width": 1})
        c.itemconfig(c_district_texts[x][y], {"text": str(district.infected)+"/"+str(district.people)})


    c.itemconfig(c_districts[x][y], {"fill": percent_to_color(infectedpercent)})


print("Created! Infecting person...")
test.infect_random_person()

stop = False
print("Done! Main loop staring...")
for day in range(0, DAYS):
    print("Day", day + 1, "started")

    print("Doing transfers...")
    test.do_close_infects()
    print("Doing local infects...")
    test.do_local_infects()

    for i in range(0, WIDTH):
        for j in range(0, HEIGHT):
            update_district_color(i, j)

    print("Updating window...")
    root.update()

    if test.is_fully_infected():
        print("Done!")
        print("Generating stats...")
        test.generate_stats()
        print("-------------------------------")
        print("Done! Shutting down in")
        for i in range(3, -1, -1):
            print(i)
            sleep(1)
            root.update()
        break

    print("Day", day + 1, "ended")
