import random, time, pygame, sys, copy
from pygame.locals import *

FPS = 30  # frames per second to update the screen
WINDOWWIDTH = 1000  # width of the program's window, in pixels
WINDOWHEIGHT = 600  # height in pixels
GEMIMAGESIZE = 64  # width & height of each space in pixels

BOARDWIDTH = 8  # how many columns in the board
BOARDHEIGHT = 8  # how many rows in the board
# NUMGEMIMAGES is the number of gem types. You will need .png image
# files named gem0.png, gem1.png, etc. up to gem(N-1).png.
NUMGEMIMAGES = 7
assert NUMGEMIMAGES >= 5  # game needs at least 5 types of gems to work

# NUMMATCHSOUNDS is the number of different sounds to choose from when
# a match is made. The .wav files are named match0.wav, match1.wav, etc.
NUMMATCHSOUNDS = 6

# setting up the screen dimensions
DISPLAY = pygame.display.set_mode((1000, 600), 0, 32)
screen = DISPLAY
# setting up the screen dimensions
RECT = pygame.draw.rect(DISPLAY, (0, 0, 255), (20, 20, 160, 160))

MOVERATE = 25  # 1 to 100, larger num means faster animations
DEDUCTSPEED = 0.8  # reduces score by 1 point every DEDUCTSPEED seconds.

#             R    G    B
# initializing colours to use later on.
PURPLE = (255, 0, 255)
LIGHTBLUE = (170, 190, 255)
BLUE = (0, 0, 255)
RED = (255, 100, 100)
BLACK = (0, 0, 0)
BROWN = (85, 65, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
HIGHLIGHTCOLOR = PURPLE  # color of the selected gem's border
BGCOLOR = RED  # background color on the screen
GRIDCOLOR = BLUE  # color of the game board
GAMEOVERCOLOR = RED  # color of the "Game over" text.
GAMEOVERBGCOLOR = WHITE  # background color of the "Game over" text.
SCORECOLOR = WHITE  # color of the text for the player's score

RedRectangle = pygame.draw.rect(DISPLAY, RED, (200, 150, 100, 50))

# The amount of space to the sides of the board to the edge of the window
# is used several times, so calculate it once here and store in variables.
XMARGIN = int((WINDOWWIDTH - GEMIMAGESIZE * BOARDWIDTH) / 12)
YMARGIN = int((WINDOWHEIGHT - GEMIMAGESIZE * BOARDHEIGHT) / 2)

# constants for direction values
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

EMPTY_SPACE = -1  # an arbitrary, nonpositive value used later to help create the effect of gravity
ROWABOVEBOARD = 'row above board'  # an arbitrary, non-integer value used to create "gravity" effect on pieces


# a second screen to create a different main menu for when the player clears the first level. Defining a function
def Screen2():
    # load the screen image. Transform it to the scale of the board. Transfer the image onto the new screen, then update the screen.
    screen2 = pygame.image.load('Screen2.png')
    screen2 = pygame.transform.scale(screen2, (1000, 600))
    screen.blit(screen2, (0, 0))
    pygame.display.update()
    pygame.time.wait(5000)
    # if certian keys are entered the menu will take the player to different places. m = main menu. 0 = the third screen.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                MainMenu1()
            if event.key == pygame.K_0:
                Screen3()


# load the screen image. Transform it to the scale of the board. Transfer the image onto the new screen, then update the screen.
def Screen3():
    screen3 = pygame.image.load('Screen3.png')
    screen3 = pygame.transform.scale(screen3, (1000, 600))
    screen.blit(screen3, (0, 0))
    pygame.display.update()
    pygame.time.wait(5000)

    # if certian keys are entered the menu will take the player to different places. m = main menu. 0 = the third screen.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                Screen4()
            if event.key == pygame.K_m:
                MainMenu1()


# load the screen image. Transform it to the scale of the board. Transfer the image onto the new screen, then update the screen.

def Screen4():
    screen3 = pygame.image.load('Screen4.png')
    screen3 = pygame.transform.scale(screen3, (1000, 600))
    screen.blit(screen3, (0, 0))
    pygame.display.update()
    pygame.time.wait(5000)

    # if certian keys are entered the menu will take the player to different places. m = main menu. 0 = the third screen.
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                MainMenu1()
            if event.key == pygame.K_0:
                MainMenu1()


# this is the main function which initilizes most variables and functions that stay present throughout the entire game.
def main():
    # rendering/ inputing frames per second, fonts, gem images, backrounds, and the board which is a rectangle.
    global FPSCLOCK, DISPLAYSURF, GEMIMAGES, GAMESOUNDS, BASICFONT, BOARDRECTS

    # Initial set up. including a clock window dimesions which are pre specified a capiton at the top of the screen adn the font
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Elemental Match')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 36)

    # Load the images incliding their demisnsions, their "randomness" in apperance on the board, and rendering them to the screen in the righ place
    GEMIMAGES = []
    for i in range(1, NUMGEMIMAGES + 1):
        gemImage = pygame.image.load('gem%s.png' % i)
        if gemImage.get_size() != (GEMIMAGESIZE, GEMIMAGESIZE):
            gemImage = pygame.transform.smoothscale(gemImage, (GEMIMAGESIZE, GEMIMAGESIZE))
        GEMIMAGES.append(gemImage)

    # Load the sounds.
    GAMESOUNDS = {}
    # GAMESOUNDS['bad swap'] = pygame.mixer.Sound('../TestWork/badswap.wav')
    GAMESOUNDS['match'] = []
    # plays sound randomly in a random order once a gametile is moved
    for i in range(NUMMATCHSOUNDS):
        GAMESOUNDS['match'].append(pygame.mixer.Sound('match%s.wav' % i))

    # Create pygame.Rect objects for each board space to
    # do board-coordinate-to-pixel-coordinate conversions. This allows for the animations to run smoothly
    BOARDRECTS = []
    for x in range(BOARDWIDTH):
        BOARDRECTS.append([])
        for y in range(BOARDHEIGHT):
            r = pygame.Rect((XMARGIN + (x * GEMIMAGESIZE),
                             YMARGIN + (y * GEMIMAGESIZE),
                             GEMIMAGESIZE,
                             GEMIMAGESIZE))
            BOARDRECTS[x].append(r)
    # if all of main is running and operational the program will start by running the splash screen
    while True:
        Splashs()


# this function is responsible for teh splash screen.
def Splashs():
    splash = pygame.image.load('splashscreen.jpeg')  # loads in the splashscreen image
    splash = pygame.transform.scale(splash, (1000, 600))  # renders it to fit the specified screen dimensions
    screen.blit(splash, (0, 0))  # transfers image to the screen
    pygame.display.update()  # updates the screen
    pygame.time.wait(1000)  # places teh screen on a timer (miliseconds)
    # When the timer exaughts itself this function runs the main menu function
    while True:
        MainMenu1()


# this is the main menu function which acts as the main page or the "truck of a tree" or a gateway to take you to different functions depending on the players wishes.
def MainMenu():
    mainmenu = pygame.image.load('mainscreen.png')  # loads in the main menu image image
    mainmenu = pygame.transform.scale(mainmenu, (1000, 600))  # renders it to fit the specified screen dimensions
    screen.blit(mainmenu, (0, 0))  # transfers image to the screen
    pygame.display.update()  # updates the screen

    # a list of if statments. If certian key are entered then the loop will run different functions. For example if i is entered the instructions function will run.

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                EarthLevel()
            if event.key == pygame.K_2:
                FireLevel()
            if event.key == pygame.K_3:
                IceLevel()
            if event.key == pygame.K_t:
                Screen2()
            if event.key == pygame.K_q:
                QuitScreen()
            if event.key == pygame.K_i:
                Instructions()


# this is the quit screen. if the letter q is run in the main menu it will run this function.
# this function loads a quit screen on which is on a 1 milisecond timer.
def QuitScreen():
    quitscreen = pygame.image.load('quitscreen.png')
    quitscreen = pygame.transform.scale(quitscreen, (1000, 600))
    screen.blit(quitscreen, (0, 0))
    pygame.display.update()
    # this is a 1 milisecond timer so that the user has a seamless transition out of the game
    pygame.time.wait(1)
    # when that timer exaughts itself the program will be shut off
    while True:
        pygame.quit()
        sys.exit()


# This is the first level.
def EarthLevel():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board. These variables will be draw on the baord using the drawscore variable.
    gameBoard = GetBlankBoard()
    score = 0  # starting score is 0
    movee = 14  # the player has 14 moves
    Level = str("Lv I")  # this is level 1
    # animates/ renders the board
    FillBoardAndAnimate(gameBoard, [], str(score) + str(Level))  # LMO# Drop the initial gems.
    FillBoardAndAnimate(gameBoard, [], Level)
    # loads the windowhieght, lenght and draws the game screen onto the board
    RECT = pygame.draw.rect(DISPLAY, (0, 0, 255), (30, 50, 260, 260))
    RECT = pygame.display.flip()
    RECT = True
    RECT = (10, WINDOWHEIGHT - 6)

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None
    BOARDWIDTH = 9
    BOARDHEIGHT = 9

    while True:  # while the staements above are ture run the main game loop
        # this is used to randomize the points a player recieves per match between 1 and 10
        import random
        randomscore = random.randint(1, 10)
        # this is used so that the player has the ability to leave the game at any time
        clickedSpace = None
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return  # start a new game

            # This code is the main user interface code and serves the purpose of making sure that
            # the users commands register into the game. Mainly pertaining to the movement of tiles.

            # this is used so that the player has the ability to leave the game at any time
            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return  # after games ends, click to start a new game
                    # is used to register if the user selected a game tile
                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = CheckForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = CheckForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = CheckForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = GetSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None  # deselect the first gem
                continue

            # Show the swap animation when 2 gems are selected and switch places on the screen.
            boardCopy = GetBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure inorder to properly register the gems switching places.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                GAMESOUNDS['bad swap'].play()
                # Swap the gems in the board data structure inorder to properly register the gems switching places.
                # the score varible help the swap to be registed as an addtion to players score
                AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                # Swap the gems in the board data structure inorder to properly register the gems switching places.
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        # this helps to sink the pieces swaping to the score varible
                        scoreAdd += (randomscore + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            # this helps the gems fall and replacer the gems that were matched. It also corrilates the match to the score.
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * GEMIMAGESIZE + XMARGIN,
                                       'y': gem[1] * GEMIMAGESIZE + YMARGIN})
                    random.choice(GAMESOUNDS['match']).play()
                    # these two lines add to the current score and make sure the score keeps growing and take away the amount of moves
                    # the player has left by 1, since for this program to run the player would of had to make a move
                    score += scoreAdd
                    movee = movee - 1

                    # Drop the new gems. "gravity"
                    FillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = findMatchingGems(gameBoard)
            firstSelectedGem = None
            # if the move counter has = 0 then run the gmae is over function
            if not CanMakeMove(gameBoard) or movee == 0:
                gameIsOver = True

        # Draw the background.
        img = pygame.image.load("EBackground.png")
        # displaying the background
        DISPLAYSURF.blit(img, (0, 0))
        # drawing the gameboard again
        DrawBoard(gameBoard)

        # This code is responsible for the health bar and overlaps 3 rectangles.
        # a red and yellow rectangle are behind the green refctangle.
        # as the score interger increase the green bar will get smaller showing the red bar implyign boss has less health.
        pygame.draw.rect(DISPLAY, RED, [675, 500, 255, 45])
        pygame.draw.rect(DISPLAY, YELLOW, [675, 500, 150, 45])

        EscapeButton()
        # the red turns into balck once the boss' health gets really low
        if score > 55:
            pygame.draw.rect(DISPLAY, BLACK, [675, 500, 255, 45])
        # the green health abr gets smaller by a factor of 16 units every 3 incriments the score increases
        if score < 3:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 255, 45])
        elif score >= 3 and score < 6:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 239, 45])
        elif score >= 6 and score < 9:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 223, 45])
        elif score >= 9 and score < 12:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 207, 45])
        elif score >= 12 and score < 15:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 191, 45])
        elif score >= 15 and score < 18:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 175, 45])
        elif score >= 18 and score < 21:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 159, 45])
        elif score >= 21 and score < 24:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 143, 45])
        elif score >= 24 and score < 27:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 127, 45])
        elif score >= 27 and score < 30:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 111, 45])
        elif score >= 30 and score < 33:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 95, 45])
        elif score >= 33 and score < 36:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 79, 45])
        elif score >= 36 and score < 39:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 63, 45])
        elif score >= 39 and score < 42:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 47, 45])
        elif score >= 42 and score < 45:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 31, 45])
        elif score >= 45 and score < 48:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 25, 45])
        elif score >= 48 and score < 51:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 20, 45])
        elif score >= 51 and score < 54:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 19, 45])
        elif score >= 54 and score < 57:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 15, 45])
        elif score >= 57 and score < 60:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 14, 45])
        elif score >= 60 and score < 63:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 12, 45])
        elif score >= 63 and score < 66:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 10, 45])
        elif score >= 66 and score < 69:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 5, 45])
        elif score >= 70 and score > 69:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 0, 45])

        # under main loop, highlights the selected gem

        if firstSelectedGem != None:
            highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        # if gameIsOver:

        # if clickContinueTextSurf == None:
        # Only render the text once. In future iterations, just
        # use the Surface object already in clickContinueTextSurf
        # clickContinueTextRect = clickContinueTextSurf.get_rect()
        # clickContinueTextRect.center = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)
        # DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        # draws the score board.
        DrawScore(str("Score:") + str(score) + str("    ") + str("Lvl:") + str(1) + str("  ") + str("    ") + str(
            "Moves:") + str(movee) + str("   ") + str("HS:") + str(7))
        pygame.display.update()

        FPSCLOCK.tick(FPS)
        # if the player achived a score of 70 or more before the move count is exaughsted the winscreen function appeaers.
        # if they fail to do so the lose screen fuction runs.
        if score == 70 or score > 70:
            Winscreen = pygame.image.load('winscreen.png')
            Winscreen = pygame.transform.scale(Winscreen, (1000, 600))
            screen.blit(Winscreen, (0, 0))
            pygame.display.update()
            pygame.time.wait(15000)
            while True:
                MainMenu2()
        if movee == 0:
            LoseScreen()



# This function is resposible for running the instructions
def Instructions():
    instructionss = pygame.image.load('instructions.png')  # loads in the instructions image
    instructionss = pygame.transform.scale(instructionss,
                                           (1000, 600))  # renders it to fit the specified screen dimensions
    screen.blit(instructionss, (0, 0))  # transfers image to the screen
    pygame.display.update()  # updates the screen
    pygame.time.wait(12000)  # places teh screen on a timer (miliseconds)
    # When the timer exaughts itself this function runs the main menu function
    while True:
        MainMenu1()


# This functions is responsible for running the lose screen page.
def LoseScreen():
    losescreen = pygame.image.load('losescreen.png')  # loads in the instructions image
    losescreen = pygame.transform.scale(losescreen, (1000, 600))  # renders it to fit the specified screen dimensions
    screen.blit(losescreen, (0, 0))  # transfers image to the screen
    pygame.display.update()  # updates the screen
    pygame.time.wait(15000)  # places teh screen on a timer (miliseconds)
    # When the timer exaughts itself this function runs the main menu function
    while True:
        MainMenu1()


# this is the function responsible for running the fire level
def FireLevel():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board
    gameBoard = GetBlankBoard()
    score = 0
    movee = 15
    Level = str("Lv I")
    FillBoardAndAnimate(gameBoard, [], str(score) + str(Level))  # LMO# Drop the initial gems.
    FillBoardAndAnimate(gameBoard, [], Level)
    RECT = pygame.draw.rect(DISPLAY, (0, 0, 255), (30, 50, 260, 260))
    RECT = pygame.display.flip()
    RECT = True
    RECT = (10, WINDOWHEIGHT - 6)

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    while True:  # main game loop

        import random

        randomscore = random.randint(1, 10)
        clickedSpace = None
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return  # start a new game

            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return  # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = CheckForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = CheckForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = CheckForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = GetSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None  # deselect the first gem
                continue

            # Show the swap animation on the screen.
            boardCopy = GetBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                GAMESOUNDS['bad swap'].play()
                AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (randomscore + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * GEMIMAGESIZE + XMARGIN,
                                       'y': gem[1] * GEMIMAGESIZE + YMARGIN})
                    random.choice(GAMESOUNDS['match']).play()
                    score += scoreAdd
                    movee = movee - 1

                    # Drop the new gems.
                    FillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = findMatchingGems(gameBoard)
            firstSelectedGem = None

            if not CanMakeMove(gameBoard) or movee == 0:
                gameIsOver = True

        # Draw the board.
        img = pygame.image.load("FBackground.png")

        DISPLAYSURF.blit(img, (0, 0))
        DrawBoard(gameBoard)
        pygame.draw.rect(DISPLAY, RED, [675, 500, 255, 45])
        pygame.draw.rect(DISPLAY, YELLOW, [675, 500, 150, 45])
        pygame.draw.rect(DISPLAY, GREEN, [675, 550, 255, 45])

        EscapeButton()

        if score > 55:
            pygame.draw.rect(DISPLAY, BLACK, [675, 500, 255, 45])

        if score < 3:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 255, 45])
        elif score >= 3 and score < 6:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 239, 45])
        elif score >= 6 and score < 9:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 223, 45])
        elif score >= 9 and score < 12:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 207, 45])
        elif score >= 12 and score < 15:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 191, 45])
        elif score >= 15 and score < 18:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 175, 45])
        elif score >= 18 and score < 21:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 159, 45])
        elif score >= 21 and score < 24:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 143, 45])
        elif score >= 24 and score < 27:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 127, 45])
        elif score >= 27 and score < 30:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 111, 45])
        elif score >= 30 and score < 33:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 95, 45])
        elif score >= 33 and score < 36:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 79, 45])
        elif score >= 36 and score < 39:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 63, 45])
        elif score >= 39 and score < 42:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 47, 45])
        elif score >= 42 and score < 45:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 31, 45])
        elif score >= 45 and score < 48:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 25, 45])
        elif score >= 48 and score < 51:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 20, 45])
        elif score >= 51 and score < 54:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 19, 45])
        elif score >= 54 and score < 57:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 12, 45])
        elif score >= 57 and score < 60:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 10, 45])
        elif score >= 60 and score < 63:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 0, 45])
            # second bar
        elif score >= 69 and score < 72:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 0, 45])
        elif score >= 72 and score < 75:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 15, 45])
        elif score >= 75 and score < 78:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 30, 45])
        elif score >= 78 and score < 81:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 40, 45])
        elif score >= 81 and score < 84:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 50, 45])
        elif score >= 84 and score > 87:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 70, 45])
        elif score >= 87 and score < 90:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 90, 45])
        elif score >= 90 and score < 93:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 100, 45])
        elif score >= 93 and score < 96:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 130, 45])
        elif score >= 96 and score < 99:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 150, 45])
        elif score >= 99 and score < 102:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 170, 45])
        elif score >= 102 and score > 105:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 190, 45])
        elif score >= 105 and score < 108:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 220, 45])
        elif score >= 108 and score < 110:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 230, 45])
        elif score >= 110 and score < 113:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 255, 45])

        # under main loop

        if firstSelectedGem != None:
            highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        # if gameIsOver:

        # if clickContinueTextSurf == None:
        # Only render the text once. In future iterations, just
        # use the Surface object already in clickContinueTextSurf

        # clickContinueTextRect = clickContinueTextSurf.get_rect()
        # clickContinueTextRect.center = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)
        # DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        DrawScore(str("Score:") + str(score) + str("    ") + str("Lvl:") + str(2) + str("  ") + str("    ") + str(
            "Moves:") + str(movee) + str("   ") + str("HS:") + str(7))
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        # under main loop

        if score == 110 or score > 110:
            Winscreen = pygame.image.load('winscreen.png')
            Winscreen = pygame.transform.scale(Winscreen, (1000, 600))
            screen.blit(Winscreen, (0, 0))
            pygame.display.update()
            pygame.time.wait(15000)
            while True:
                MainMenu3()
        if movee == 0:
            LoseScreen()




def IceLevel():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board
    gameBoard = GetBlankBoard()
    score = 0
    movee = 24
    Level = str("Lv I")
    FillBoardAndAnimate(gameBoard, [], str(score) + str(Level))  # LMO# Drop the initial gems.
    FillBoardAndAnimate(gameBoard, [], Level)
    RECT = pygame.draw.rect(DISPLAY, (0, 0, 255), (30, 50, 260, 260))
    RECT = pygame.display.flip()
    RECT = True
    RECT = (10, WINDOWHEIGHT - 6)

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    while True:  # main game loop

        import random

        randomscore = random.randint(1, 10)
        clickedSpace = None
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_BACKSPACE:
                return  # start a new game

            elif event.type == MOUSEBUTTONUP:
                if gameIsOver:
                    return  # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = CheckForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = CheckForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = CheckForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = GetSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None  # deselect the first gem
                continue

            # Show the swap animation on the screen.
            boardCopy = GetBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                GAMESOUNDS['bad swap'].play()
                AnimateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (randomscore + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * GEMIMAGESIZE + XMARGIN,
                                       'y': gem[1] * GEMIMAGESIZE + YMARGIN})
                    random.choice(GAMESOUNDS['match']).play()
                    score += scoreAdd
                    movee = movee - 1

                    # Drop the new gems.
                    FillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = findMatchingGems(gameBoard)
            firstSelectedGem = None

            if not CanMakeMove(gameBoard) or movee == 0:
                gameIsOver = True

        # Draw the board.
        img = pygame.image.load("IBackground.png")

        DISPLAYSURF.blit(img, (0, 0))
        DrawBoard(gameBoard)
        pygame.draw.rect(DISPLAY, RED, [675, 500, 255, 45])
        pygame.draw.rect(DISPLAY, YELLOW, [675, 500, 150, 45])
        pygame.draw.rect(DISPLAY, GREEN, [675, 550, 255, 45])

        EscapeButton()

        if score > 55:
            pygame.draw.rect(DISPLAY, BLACK, [675, 500, 255, 45])

        if score < 3:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 255, 45])
        elif score >= 3 and score < 6:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 239, 45])
        elif score >= 6 and score < 9:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 223, 45])
        elif score >= 9 and score < 12:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 207, 45])
        elif score >= 12 and score < 15:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 191, 45])
        elif score >= 15 and score < 18:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 175, 45])
        elif score >= 18 and score < 21:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 159, 45])
        elif score >= 21 and score < 24:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 143, 45])
        elif score >= 24 and score < 27:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 127, 45])
        elif score >= 27 and score < 30:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 111, 45])
        elif score >= 30 and score < 33:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 95, 45])
        elif score >= 33 and score < 36:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 79, 45])
        elif score >= 36 and score < 39:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 63, 45])
        elif score >= 39 and score < 42:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 47, 45])
        elif score >= 42 and score < 45:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 31, 45])
        elif score >= 45 and score < 48:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 25, 45])
        elif score >= 48 and score < 51:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 20, 45])
        elif score >= 51 and score < 54:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 19, 45])
        elif score >= 54 and score < 57:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 12, 45])
        elif score >= 57 and score < 60:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 10, 45])
        elif score >= 60 and score < 63:
            pygame.draw.rect(DISPLAY, GREEN, [675, 500, 0, 45])
            # second bar
        elif score >= 69 and score < 72:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 0, 45])
        elif score >= 72 and score < 75:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 15, 45])
        elif score >= 75 and score < 78:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 30, 45])
        elif score >= 78 and score < 81:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 40, 45])
        elif score >= 81 and score < 84:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 50, 45])
        elif score >= 84 and score > 87:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 70, 45])
        elif score >= 87 and score < 90:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 100, 45])
        elif score >= 90 and score < 93:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 130, 45])
        elif score >= 93 and score < 96:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 160, 45])
        elif score >= 96 and score < 99:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 190, 45])
        elif score >= 99 and score < 102:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 215, 45])
        elif score >= 102 and score > 105:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 220, 45])
        elif score >= 105 and score < 108:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 240, 45])
        elif score >= 108 and score < 110:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 250, 45])
        elif score >= 110 and score < 113:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 255, 45])
            # bar three last leg
        elif score >= 114 and score < 180:
            pygame.draw.rect(DISPLAY, RED, [675, 550, 255, 45])

        elif score >= 150 and score < 180:
            pygame.draw.rect(DISPLAY, BLACK, [675, 550, 255, 45])

        elif score >= 114 and score < 180:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 255, 45])
        elif score >= 72 and score < 75:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 230, 45])
        elif score >= 75 and score < 78:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 220, 45])
        elif score >= 78 and score < 81:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 200, 45])
        elif score >= 81 and score < 84:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 190, 45])
        elif score >= 84 and score > 87:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 170, 45])
        elif score >= 87 and score < 90:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 150, 45])
        elif score >= 90 and score < 93:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 130, 45])
        elif score >= 93 and score < 96:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 110, 45])
        elif score >= 96 and score < 99:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 90, 45])
        elif score >= 99 and score < 102:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 80, 45])
        elif score >= 102 and score > 105:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 60, 45])
        elif score >= 105 and score < 108:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 30, 45])
        elif score >= 108 and score < 110:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 15, 45])
        elif score >= 110 and score < 113:
            pygame.draw.rect(DISPLAY, GREEN, [675, 550, 0, 45])

        # under main loop

        if firstSelectedGem != None:
            highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        # if gameIsOver:

        # if clickContinueTextSurf == None:
        # Only render the text once. In future iterations, just
        # use the Surface object already in clickContinueTextSurf
        # clickContinueTextRect = clickContinueTextSurf.get_rect()
        # clickContinueTextRect.center = int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2)
        # DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        DrawScore(str("Score:") + str(score) + str("    ") + str("Lvl:") + str(3) + str("  ") + str("    ") + str(
            "Moves:") + str(movee) + str("   ") + str("HS:") + str(7))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if score == 170 or score > 170:
            Congrats = pygame.image.load('congrats.png')
            Congrats = pygame.transform.scale(Congrats, (1000, 600))
            screen.blit(Congrats, (0, 0))
            pygame.display.update()
            pygame.time.wait(3000)
            while True:
                MainMenu4()
        if movee == 0:
            LoseScreen()



def GetSwappingGems(board, firstXY, secondXY):
    # If the gems at the (X, Y) coordinates of the two gems are adjacent,
    # then their 'direction' keys are set to the appropriate direction
    # value to be swapped with each other.
    # Otherwise, (None, None) is returned.
    firstGem = {'imageNum': board[firstXY['x']][firstXY['y']],
                'x': firstXY['x'],
                'y': firstXY['y']}
    secondGem = {'imageNum': board[secondXY['x']][secondXY['y']],
                 'x': secondXY['x'],
                 'y': secondXY['y']}
    highlightedGem = None
    if firstGem['x'] == secondGem['x'] + 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = LEFT
        secondGem['direction'] = RIGHT
    elif firstGem['x'] == secondGem['x'] - 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = RIGHT
        secondGem['direction'] = LEFT
    elif firstGem['y'] == secondGem['y'] + 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = UP
        secondGem['direction'] = DOWN
    elif firstGem['y'] == secondGem['y'] - 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = DOWN
        secondGem['direction'] = UP
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return firstGem, secondGem


def GetSwappingGems(board, firstXY, secondXY):
    # If the gems at the (X, Y) coordinates of the two gems are adjacent,
    # then their 'direction' keys are set to the appropriate direction
    # value to be swapped with each other.
    # Otherwise, (None, None) is returned.
    firstGem = {'imageNum': board[firstXY['x']][firstXY['y']],
                'x': firstXY['x'],
                'y': firstXY['y']}
    secondGem = {'imageNum': board[secondXY['x']][secondXY['y']],
                 'x': secondXY['x'],
                 'y': secondXY['y']}
    highlightedGem = None
    if firstGem['x'] == secondGem['x'] + 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = LEFT
        secondGem['direction'] = RIGHT
    elif firstGem['x'] == secondGem['x'] - 1 and firstGem['y'] == secondGem['y']:
        firstGem['direction'] = RIGHT
        secondGem['direction'] = LEFT
    elif firstGem['y'] == secondGem['y'] + 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = UP
        secondGem['direction'] = DOWN
    elif firstGem['y'] == secondGem['y'] - 1 and firstGem['x'] == secondGem['x']:
        firstGem['direction'] = DOWN
        secondGem['direction'] = UP
    else:
        # These gems are not adjacent and can't be swapped.
        return None, None
    return firstGem, secondGem


def GetBlankBoard():
    # Create and return a blank board data structure.
    board = []
    for x in range(
            BOARDWIDTH):  # the board width is 8 and this code goes through every integer between 1 and 8 and the same for the hieght of the board
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    return board


def CanMakeMove(board):
    # Return True if the board is in a state where a matching
    # move can be made on it. Otherwise return False.

    # The patterns in oneOffPatterns represent gems that are configured
    # in a way where it only takes one move to make a triplet.
    # these are the possible patterns that are required to make a triplet or a match
    oneOffPatterns = (((0, 1), (1, 0), (2, 0)),
                      ((0, 1), (1, 1), (2, 0)),
                      ((0, 0), (1, 1), (2, 0)),
                      ((0, 1), (1, 0), (2, 1)),
                      ((0, 0), (1, 0), (2, 1)),
                      ((0, 0), (1, 1), (2, 1)),
                      ((0, 0), (0, 2), (0, 3)),
                      ((0, 0), (0, 1), (0, 3)))
    # these patterns can pertain to height or width
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            for pat in oneOffPatterns:
                # check each possible pattern of "match in next move" to
                # see if a possible move can be made.
                if (getGemAt(board, x + pat[0][0], y + pat[0][1]) == \
                    getGemAt(board, x + pat[1][0], y + pat[1][1]) == \
                    getGemAt(board, x + pat[2][0], y + pat[2][1]) != None) or \
                        (getGemAt(board, x + pat[0][1], y + pat[0][0]) == \
                         getGemAt(board, x + pat[1][1], y + pat[1][0]) == \
                         getGemAt(board, x + pat[2][1], y + pat[2][0]) != None):
                    return True  # return True the first time you find a pattern
    return False


def DrawMovingGem(gem, progress):
    # Draw a gem sliding in the direction that its 'direction' key
    # indicates. The progress parameter is a number from 0 (just
    # starting) to 100 (slide complete).
    movex = 0
    movey = 0
    progress *= 0.01

    # these line of code dictate that the gem coresoponds to the direction the user chooses to switch them
    # if the user moves the gem up the gem moves upwards and the other moves downwards
    if gem['direction'] == UP:
        movey = -int(progress * GEMIMAGESIZE)
    elif gem['direction'] == DOWN:
        movey = int(progress * GEMIMAGESIZE)
    elif gem['direction'] == RIGHT:
        movex = int(progress * GEMIMAGESIZE)
    elif gem['direction'] == LEFT:
        movex = -int(progress * GEMIMAGESIZE)

    # these are for the row above the board which helps create the illusion of gravity when they fall downwards
    basex = gem['x']
    basey = gem['y']
    if basey == ROWABOVEBOARD:
        basey = -1
    # these are for the row above the board which helps create the illusion of gravity when they fall downwards
    pixelx = XMARGIN + (basex * GEMIMAGESIZE)
    pixely = YMARGIN + (basey * GEMIMAGESIZE)
    # this combinds all the neccisary code for gravity and places them in one variable.
    r = pygame.Rect((pixelx + movex, pixely + movey, GEMIMAGESIZE, GEMIMAGESIZE))
    DISPLAYSURF.blit(GEMIMAGES[gem['imageNum']], r)


# this is the function responsible for the illiusion of gravity in our game
def pullDownAllGems(board):
    # pulls down gems on the board to the bottom to fill in any gaps
    for x in range(BOARDWIDTH):
        gemsInColumn = []
        # this goes through the board vertically searching for empty spaces and if there are any then it causes the rowabove the board to fall
        for y in range(BOARDHEIGHT):
            if board[x][y] != EMPTY_SPACE:
                gemsInColumn.append(board[x][y])
        board[x] = ([EMPTY_SPACE] * (BOARDHEIGHT - len(gemsInColumn))) + gemsInColumn


def getGemAt(board, x, y):
    if x < 0 or y < 0 or x >= BOARDWIDTH or y >= BOARDHEIGHT:
        return None
    else:
        return board[x][y]


# this function is responsible for initializing the gems on the board
def getDropSlots(board):
    # Creates a "drop slot" for each column and fills the slot with a
    # number of gems that that column is lacking. This function assumes
    # that the gems have been gravity dropped already.
    boardCopy = copy.deepcopy(board)
    pullDownAllGems(boardCopy)

    dropSlots = []
    for i in range(BOARDWIDTH):
        dropSlots.append([])

    # count the number of empty spaces in each column on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT - 1, -1, -1):  # start from bottom, going up
            if boardCopy[x][y] == EMPTY_SPACE:
                possibleGems = list(range(len(GEMIMAGES)))
                for offsetX, offsetY in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                    # Narrow down the possible gems we should put in the
                    # blank space so we don't end up putting an two of
                    # the same gems next to each other when they drop.
                    neighborGem = getGemAt(boardCopy, x + offsetX, y + offsetY)
                    if neighborGem != None and neighborGem in possibleGems:
                        possibleGems.remove(neighborGem)

                newGem = random.choice(possibleGems)
                boardCopy[x][y] = newGem
                dropSlots[x].append(newGem)
    return dropSlots


# this function is responsible for finsing matches
def findMatchingGems(board):
    gemsToRemove = []  # a list of lists of gems in matching triplets that should be removed
    boardCopy = copy.deepcopy(board)

    # loop through each space, checking for 3 adjacent identical gems
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            # look for horizontal matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x + 1, y) == getGemAt(boardCopy, x + 2, y) and getGemAt(
                    boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x + offset, y) == targetGem:
                    # keep checking if there's more than 3 gems in a row
                    removeSet.append((x + offset, y))
                    boardCopy[x + offset][y] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

            # look for vertical matches
            if getGemAt(boardCopy, x, y) == getGemAt(boardCopy, x, y + 1) == getGemAt(boardCopy, x, y + 2) and getGemAt(
                    boardCopy, x, y) != EMPTY_SPACE:
                targetGem = boardCopy[x][y]
                offset = 0
                removeSet = []
                while getGemAt(boardCopy, x, y + offset) == targetGem:
                    # keep checking, in case there's more than 3 gems in a row
                    removeSet.append((x, y + offset))
                    boardCopy[x][y + offset] = EMPTY_SPACE
                    offset += 1
                gemsToRemove.append(removeSet)

    return gemsToRemove


# this code highlights the tiles once they are selected
def highlightSpace(x, y):
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, BOARDRECTS[x][y], 4)


# this function is responsible for gravity
def getDroppingGems(board):
    # Find all the gems that have an empty space below them
    boardCopy = copy.deepcopy(board)
    droppingGems = []
    for x in range(BOARDWIDTH):  # this code goes throught the board horizontally and replaces all missing tiles
        for y in range(BOARDHEIGHT - 2, -1, -1):
            if boardCopy[x][y + 1] == EMPTY_SPACE and boardCopy[x][y] != EMPTY_SPACE:
                # This space drops if not empty but the space below it is
                droppingGems.append({'imageNum': boardCopy[x][y], 'x': x, 'y': y, 'direction': DOWN})
                boardCopy[x][y] = EMPTY_SPACE
    return droppingGems


def AnimateMovingGems(board, gems, pointsText, score):
    # pointsText is a dictionary with keys 'x', 'y', and 'points'
    progress = 0  # progress at 0 represents beginning, 100 means finished.
    while progress < 100:  # animation loop
        DISPLAYSURF.fill(BGCOLOR)
        DrawBoard(board)
        for gem in gems:  # Draw each gem.
            DrawMovingGem(gem, progress)
        DrawScore(score)
        for pointText in pointsText:
            pointsSurf = BASICFONT.render(str(pointText['points']), 1, SCORECOLOR)
            pointsRect = pointsSurf.get_rect()
            pointsRect.center = (pointText['x'], pointText['y'])
            DISPLAYSURF.blit(pointsSurf, pointsRect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        progress += MOVERATE  # progress the animation a little bit more for the next frame


# this function is responsible fot the movement of gems
def MoveGems(board, movingGems):
    # movingGems is a list of dicts with keys x, y, direction, imageNum
    # if certian directions are entered the gem transfers 1 place on the grid on either the x or y axis
    for gem in movingGems:
        if gem['y'] != ROWABOVEBOARD:
            board[gem['x']][gem['y']] = EMPTY_SPACE
            movex = 0
            movey = 0
            if gem['direction'] == LEFT:
                movex = -1
            elif gem['direction'] == RIGHT:
                movex = 1
            elif gem['direction'] == DOWN:
                movey = 1
            elif gem['direction'] == UP:
                movey = -1
            board[gem['x'] + movex][gem['y'] + movey] = gem['imageNum']
        else:
            # gem is located above the board (where new gems come from)
            board[gem['x']][0] = gem['imageNum']  # move to top row
            # this function draws the rectangle aroung the gems/ the grid and fills it in

        def RECT():
            pygame.init()

            WHITE = (255, 255, 255)
            BLUE = (0, 0, 255)

            DISPLAY.fill(WHITE)

            pygame.draw.rect(DISPLAY, BLACK, (200, 150, 100, 50))


# this function is responsible for gravity
# this function is called when there are empty spaces on the board
def FillBoardAndAnimate(board, points, score):
    dropSlots = getDropSlots(board)
    while dropSlots != [[]] * BOARDWIDTH:
        # do the dropping animation as long as there are more gems to drop, there are always more gems to drop
        movingGems = getDroppingGems(board)
        for x in range(len(dropSlots)):  # goes through the possible drop points 1 through 8 seeing which ones are empty
            if len(dropSlots[x]) != 0:
                # cause the lowest gem in each slot to begin moving in the DOWN direction
                movingGems.append({'imageNum': dropSlots[x][0], 'x': x, 'y': ROWABOVEBOARD, 'direction': DOWN})
        # removes teh already matdched gems from the board and makes sure they disapear, then adds to the points and score
        boardCopy = GetBoardCopyMinusGems(board, movingGems)
        AnimateMovingGems(boardCopy, movingGems, points, score)
        MoveGems(board, movingGems)

        # Make the next row of gems from the drop slots
        # the lowest by deleting the previous lowest gems.
        for x in range(len(dropSlots)):
            if len(dropSlots[x]) == 0:
                continue
            board[x][0] = dropSlots[x][0]
            del dropSlots[x][0]


# this function checks for gems that have been selected by the user
def CheckForGemClick(pos):
    # See if the mouse click was on the board
    for x in range(BOARDWIDTH):  # goes through all integers on board width 1 through 8
        for y in range(BOARDHEIGHT):  # goes through all integers on board length 1 through 8
            if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):  # tracks where the user clicks ther mouse
                return {'x': x, 'y': y}
    return None  # Click was not on the board.


# this function is responsible for displaying the board on the screen and putting it together
def DrawBoard(board):
    for x in range(BOARDWIDTH):  # goes through all integers on board width 1 through 8
        for y in range(BOARDHEIGHT):  # goes through all integers on board length 1 through 8
            pygame.draw.rect(DISPLAYSURF, GRIDCOLOR, BOARDRECTS[x][y], 1)  # displays the board and grid onto the screen
            gemToDraw = board[x][y]  # displays teh initial gems
            if gemToDraw != EMPTY_SPACE:  # draws gems into empty spaces
                DISPLAYSURF.blit(GEMIMAGES[gemToDraw], BOARDRECTS[x][y])  # transfers this new image onto the screen


# This function Creates and returns a copy of the passed board data structure
# it gets rid of them gems on a copy of the board in order to not move the board when gems move
# it is finally used in variables that only effect the board structure and not gems
def GetBoardCopyMinusGems(board, gems):
    # with the gems in the "gems" list removed from it.
    # Gems is a list of dicts, with keys x, y, direction, imageNum
    boardCopy = copy.deepcopy(board)
    # Remove some of the gems from this board data structure copy.
    for gem in gems:
        if gem['y'] != ROWABOVEBOARD:
            boardCopy[gem['x']][gem['y']] = EMPTY_SPACE
    return boardCopy


# this function is used to draw the score board
def DrawScore(score):
    scoreImg = BASICFONT.render(str(score), 1, SCORECOLOR)  # renders the text into a font
    scoreRect = scoreImg.get_rect()  # gathers a rectangle for the score to be in
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 6)  # dictates where the score will be locates
    DISPLAYSURF.blit(scoreImg, scoreRect, )  # displays the score to the screen


# this fucntion is used to reach the main menu while in a level
def EscapeButton():
    Escape = pygame.Rect(890, 5, 100, 40)  # draws a rectangle
    Escape = pygame.draw.rect(screen, RED, Escape)  # makes the rectangle red and appear on the screen
    textsurface = BASICFONT.render('Menu', True, BLACK)  # makes the text black, and renders the text
    screen.blit(textsurface, (890, 5))  # places the new image onto the screen
    pos = pygame.mouse.get_pos()  # tracks the positions of the players mouse
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # Check if the rect collided with the mouse pos
    # and if the left mouse button was pressed.
    if Escape.collidepoint(pos) and pressed1:
        Splashs()

def MainMenu1():
   mainmenu = pygame.image.load('MainMenu1.png')
   mainmenu = pygame.transform.scale(mainmenu, (1000, 600))
   screen.blit(mainmenu, (0, 0))
   pygame.display.update()

   for event in pygame.event.get():

       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_1:
               EarthLevel()
           if event.key == pygame.K_t:
               Screen2()
           if event.key == pygame.K_q:
               QuitScreen()
           if event.key == pygame.K_i:
               Instructions()

def MainMenu2():
   mainmenu = pygame.image.load('MainMenu2.png')
   mainmenu = pygame.transform.scale(mainmenu, (1000, 600))
   screen.blit(mainmenu, (0, 0))
   pygame.display.update()

   for event in pygame.event.get():

       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_1:
               EarthLevel()
           if event.key == pygame.K_2:
               FireLevel()
           if event.key == pygame.K_t:
               Screen2()
           if event.key == pygame.K_q:
               QuitScreen()
           if event.key == pygame.K_i:
               Instructions()

def MainMenu3():
   mainmenu = pygame.image.load('MainMenu3.png')
   mainmenu = pygame.transform.scale(mainmenu, (1000, 600))
   screen.blit(mainmenu, (0, 0))
   pygame.display.update()

   for event in pygame.event.get():

       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_1:
               EarthLevel()
           if event.key == pygame.K_2:
               FireLevel()
           if event.key == pygame.K_3:
               IceLevel()
           if event.key == pygame.K_t:
               Screen2()
           if event.key == pygame.K_q:
               QuitScreen()
           if event.key == pygame.K_i:
               Instructions()



def MainMenu4():
   mainmenu = pygame.image.load('MainMenu4.png')
   mainmenu = pygame.transform.scale(mainmenu, (1000, 600))
   screen.blit(mainmenu, (0, 0))
   pygame.display.update()

   for event in pygame.event.get():

       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_1:
               EarthLevel()
           if event.key == pygame.K_2:
               FireLevel()
           if event.key == pygame.K_3:
               IceLevel()
           if event.key == pygame.K_t:
               Screen2()
           if event.key == pygame.K_q:
               QuitScreen()
           if event.key == pygame.K_i:
               Instructions()




# end of the main loop
if __name__ == '__main__':
    main()

