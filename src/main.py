import pygame
import constants
import time
import random
import requests
import tkinter
import tkinter.messagebox
import traceback

try:
    pygame.init()
    pygame.mixer.init()
    FPS = 30
    WIDTH = 480
    HEIGHT = 360
    WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
    ICON = pygame.image.load("./assets/img/icons.png")
    PLAYER_WIDTH = 61
    PLAYER_HEIGHT = 92.5
    ObstacleSpawnSpeed = 1
    ObstacleMaxWaitBeforeSpawn = 10


    class Wait:
        def __init__(self, seconds, FunctionToCall, *args):
            self.func = FunctionToCall
            self.arguments = args
            self.called = False
            self.time = time.time() + seconds

        def check(self):
            if time.time() >= self.time and not (self.called):
                self.called = True
                self.func(self.arguments)
            else:
                pass


    class Object:
        def __init__(self, CostumeImages, CostumeNumber, x, y):
            self.player_image_number = CostumeNumber
            self.player_image_assets = CostumeImages
            self.player_image = pygame.image.load(
                CostumeImages[self.player_image_number])
            self.x = x
            self.y = y
            self.HALFWIDTH = round(WIDTH/2)
            self.HALFHEIGHT = round(HEIGHT/2)
            self.imageWidth = self.player_image.get_width()
            self.imageHeight = self.player_image.get_height()
            self.imageScaleRatioWidth = 0
            self.imageScaleRatioHeight = 0
            self.direction = 0
            self.hitbox = None
            self.hitboxWidth = None
            self.hitboxHeight = None
            self.hitboxXOffset = None
            self.hitboxYOffset = None
            self.mask = None

        def __getX(self):
            return self.x+self.HALFWIDTH-(self.player_image.get_width()/2)

        def __getY(self):
            return self.HALFHEIGHT-self.y-(self.player_image.get_height()/2)

        def CreateHitbox(self, width, height, xOffset=0, yOffset=0):
            self.mask = None
            self.hitbox = pygame.Rect(
                round(self.__getX())+xOffset, round(self.__getY())+yOffset, width, height)
            self.hitboxWidth = width
            self.hitboxHeight = height
            self.hitboxXOffset = xOffset
            self.hitboxYOffset = yOffset

        def CreateMask(self):
            self.hitbox = None
            self.hitboxWidth = None
            self.hitboxHeight = None
            self.hitboxXOffset = None
            self.hitboxYOffset = None
            self.mask = pygame.mask.from_surface(self.player_image)

        def ResizeSprite(self, width, height):
            self.imageScaleRatioWidth = round(self.player_image.get_width()/width)
            self.imageScaleRatioHeight = round(
                self.player_image.get_height()/height)
            self.player_image = pygame.transform.scale(
                self.player_image, (width, height))
            self.imageWidth = width
            self.imageHeight = height

        def RotateSprite(self, angleOfRotation):
            self.player_image = pygame.transform.rotate(
                self.player_image, 0-angleOfRotation)
            self.direction -= angleOfRotation

        def TouchingHitbox(self, hitbox):
            return self.hitbox.colliderect(hitbox)

        def TouchingMask(self, mask, x, y):
            offset = (round(self.x - x), round(self.y - y))
            touching = mask.overlap(self.mask, offset)
            if touching:
                return True
            else:
                return False

        def DrawSprite(self, hitbox=False):
            WINDOW.blit(self.player_image, (self.__getX(), self.__getY()))
            if self.hitbox:
                self.hitbox.x = round(self.__getX())+self.hitboxXOffset
                self.hitbox.y = round(self.__getY())+self.hitboxYOffset
            if hitbox:
                pygame.draw.rect(WINDOW, constants.RED, self.hitbox, 2)

        def SwitchCostume(self, costumeNumber):
            self.player_image_number = costumeNumber
            self.player_image = pygame.image.load(
                self.player_image_assets[self.player_image_number])
            self.player_image = pygame.transform.scale(
                self.player_image, (self.player_image.get_width()/self.imageScaleRatioWidth, self.player_image.get_height()/self.imageScaleRatioHeight))
            self.player_image = pygame.transform.rotate(
                self.player_image, self.direction)
            if self.mask:
                self.mask = pygame.mask.from_surface(self.player_image)

        def NextCostume(self):
            self.player_image_number = (
                self.player_image_number+1) % len(self.player_image_assets)
            self.SwitchCostume(self.player_image_number)


    class Background:
        def __init__(self, BackgroundImage, color=True):
            self.BackgroundImage = BackgroundImage
            self.isColor = color
            if self.isColor:
                pass
            else:
                self.BackgroundImage = pygame.image.load(self.BackgroundImage)
                self.BackgroundImage = pygame.transform.scale(
                    self.BackgroundImage, (WIDTH, HEIGHT))

        def DrawBackground(self):
            if self.isColor:
                WINDOW.fill(self.BackgroundImage)
            else:
                WINDOW.fill(constants.WHITE)
                WINDOW.blit(self.BackgroundImage, (0, 0))

        def ChangeBackground(self, BackgroundImage, color=True):
            self.__init__(BackgroundImage, color)


    class Text:
        def __init__(self, Font, FontSize):
            self.Font = pygame.font.Font(Font, FontSize)
            self.HALFWIDTH = round(WIDTH/2)
            self.HALFHEIGHT = round(HEIGHT/2)

        def DrawText(self, text, colour, x, y):
            TextToRender = self.Font.render(text, True, colour)
            WINDOW.blit(TextToRender, (x+self.HALFWIDTH-(TextToRender.get_width()/2),
                        self.HALFHEIGHT-y-(TextToRender.get_height()/2)))


    class Player(Object):
        def __init__(self, CostumeImages, CostumeNumber, x, y):
            super().__init__(CostumeImages, CostumeNumber, x, y)
            self.SPEED = 10

        def HandlePlayerMovement(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.y + self.SPEED < 196:
                self.y += self.SPEED
            if keys[pygame.K_DOWN] and self.y - self.SPEED > -194:
                self.y -= self.SPEED


    class Obstacle(Object):
        def __init__(self, CostumeImages, CostumeNumber, x, y):
            super().__init__(CostumeImages, CostumeNumber, x, y)
            self.EDGE = -205

        def move(self):
            self.x -= ObstacleSpawnSpeed

        def TouchingEdge(self):
            if self.x < self.EDGE:
                return True
            else:
                return False


    class Button(Object):
        def __init__(self, CostumeImages, CostumeNumber, x, y, onclick, text, font):
            super().__init__(CostumeImages, CostumeNumber, x, y)
            self.Onclick = onclick
            self.text = text
            self.font = font

        def HandleMouse(self):
            mouseInput = pygame.mouse.get_pressed()
            mousePos = pygame.mouse.get_pos()
            mouseHitbox = pygame.Rect(mousePos[0], mousePos[1], 1, 1)
            if self.TouchingHitbox(mouseHitbox):
                self.SwitchCostume(1)
                if mouseInput[constants.M_LEFT]:
                    self.Onclick()
            else:
                self.SwitchCostume(0)
        
        def DrawSprite(self, hitbox=False):
            super().DrawSprite(hitbox)
            self.font.DrawText(self.text, constants.BLACK, self.x, self.y)


    class BackgroundMusic:
        def __init__(self, fileName):
            pygame.mixer.music.load(fileName)

        def PlaySound(self, Repetitions, Volume=1.0):
            pygame.mixer.music.set_volume(Volume)
            pygame.mixer.music.play(Repetitions, 0)

        def ForeverPlaySound(self, Volume=1.0):
            self.PlaySound(-1, Volume)


    def ScreenRefresh(mode):
        global Obstacles
        if mode == "Game":
            Backdrop.DrawBackground()
            for entity in Obstacles:
                entity.DrawSprite()
            RocketShip.DrawSprite()
            MediumFont.DrawText(f"Score: {score}", constants.ORANGE, 185, 155)
        elif mode == "GameOver":
            Backdrop.DrawBackground()
            BigFont.DrawText("Game Over", constants.BLACK, 0, 95)
            MediumFont.DrawText(f"Score: {score}", constants.BLACK, 0, 20)
            MainMenuButton.DrawSprite()
        elif mode == "MainMenu":
            Backdrop.DrawBackground()
            BigFont.DrawText("Avoid The Obstacle", constants.BLACK, 0, 140)
            PlayButton.DrawSprite()
            LeaderBoardButton.DrawSprite()
        elif mode == "Leaderboard":
            Backdrop.DrawBackground()
            BigFont.DrawText("Leaderboard", constants.BLACK, 0, 100)
            MediumFont.DrawText(f"Score: {HighScore}", constants.BLACK, 0, 0)
            if Offline:
                MediumFont.DrawText("You Are Offline, Score Not Synced", constants.BLACK, 0, -30)
            MainMenuButton.DrawSprite()  


    def SpawnObstacle(event=None):
        global Obstacles, Spawnner
        Obstacles.append(Obstacle(["./assets/img/Obstacle-a.png"], 0,
                        200, random.randint(-188, 188)))
        Obstacles[len(Obstacles)-1].ResizeSprite(74, 33)
        Obstacles[len(Obstacles)-1].CreateHitbox(34, 32)
        Spawnner = Wait(random.uniform(
            0.001, ObstacleMaxWaitBeforeSpawn), SpawnObstacle)


    def IncreaseDifficulty(event=None):
        global DifficultyIncrease, ObstacleSpawnSpeed, ObstacleMaxWaitBeforeSpawn
        ObstacleSpawnSpeed += random.randint(1, 5)
        ObstacleMaxWaitBeforeSpawn -= random.uniform(0.001, ObstacleSpawnSpeed)
        if ObstacleMaxWaitBeforeSpawn < 1:
            ObstacleMaxWaitBeforeSpawn = 1
        DifficultyIncrease = Wait(30, IncreaseDifficulty)


    def HandleObstacle():
        global Obstacles
        DifficultyIncrease.check()
        Spawnner.check()
        for entity in Obstacles:
            entity.move()
            if entity.TouchingEdge():
                Obstacles.remove(entity)
            elif entity.TouchingHitbox(RocketShip.hitbox):
                GameOver()


    def IncreaseScore(event=None):
        global score, ScoreCounter
        score += 1
        ScoreCounter = Wait(0.1, IncreaseScore)


    def NextCostume(event=None):
        global SwitchCostume
        RocketShip.NextCostume()
        SwitchCostume = Wait(0.15, NextCostume)


    def GameOver():
        global mode, Obstacles, HighScore
        mode = "GameOver"
        if score > HighScore:
            Backdrop.ChangeBackground(constants.BLACK)
            Backdrop.DrawBackground()
            BigFont.DrawText("New High Score!", constants.WHITE, 0, 50)
            MediumFont.DrawText("Saving Score...", constants.WHITE, 0, -50)
            pygame.display.update()
            HighScore = score
            global Offline
            if not Offline:
                try:
                    requests.get(f"https://api.albloh2.repl.co/legacy/db/set/W5CLEFU9WDKS95TP/{score}")
                except:
                    Offline = True
            else:
                MediumFont.DrawText("Failed To Sync With Server.", constants.WHITE, 0, -75)
            pygame.display.update()
            pygame.time.delay(1000)
        Obstacles = []
        Backdrop.ChangeBackground(constants.ORANGE)


    def Game():
        global ScoreCounter, DifficultyIncrease, SwitchCostume, Obstacles, score, mode, ObstacleSpawnSpeed, ObstacleMaxWaitBeforeSpawn
        mode = "Game"
        ObstacleSpawnSpeed = 1
        ObstacleMaxWaitBeforeSpawn = 10
        RocketShip.y = 0
        Backdrop.ChangeBackground("./assets/img/GameScreen.png", False)
        DifficultyIncrease = Wait(30, IncreaseDifficulty)
        ScoreCounter = Wait(0.1, IncreaseScore)
        SwitchCostume = Wait(0.15, NextCostume)
        Obstacles = []
        score = 0
        SpawnObstacle()


    def MainMenu():
        global mode
        mode = "MainMenu"
        Backdrop.ChangeBackground(constants.GREEN)

    def LeaderBoard():
        global mode
        mode = "Leaderboard"
        Backdrop.ChangeBackground(constants.CYAN)

    pygame.display.set_caption("Avoid The Obstacle")
    pygame.display.set_icon(pygame.transform.scale(ICON, (32, 32)))
    BigFont = Text("./assets/fonts/font.otf", 48)
    MediumFont = Text("./assets/fonts/font.otf", 24)
    SmallFont = Text("./assets/fonts/font.otf", 18)
    BigFont.DrawText("Ellipsis Gaming", constants.WHITE, 0, 0)
    pygame.display.update()
    pygame.time.delay(1000)
    Bgm = BackgroundMusic("./assets/sfx/ThemeMusic.mp3")
    Bgm.ForeverPlaySound()
    Backdrop = Background("./assets/img/GameScreen.png", False)
    RocketShip = Player(("./assets/img/Rocketship-a.png", "./assets/img/Rocketship-b.png",
                        "./assets/img/Rocketship-c.png", "./assets/img/Rocketship-d.png"), 0, -184, 0)
    RocketShip.ResizeSprite(PLAYER_WIDTH, PLAYER_HEIGHT)
    RocketShip.RotateSprite(90)
    RocketShip.CreateHitbox(83, 52)
    MainMenuButton = Button(["./assets/img/Button-a.png",
                    "./assets/img/Button-b.png"], 0, 0, -100, MainMenu, "Back", MediumFont)
    MainMenuButton.ResizeSprite(120, 53)
    MainMenuButton.CreateHitbox(MainMenuButton.imageWidth, MainMenuButton.imageHeight)
    PlayButton = Button(["./assets/img/Button-a.png",
                    "./assets/img/Button-b.png"], 0, 0, 50, Game, "Play", MediumFont)
    PlayButton.ResizeSprite(120, 53)
    PlayButton.CreateHitbox(PlayButton.imageWidth, PlayButton.imageHeight)
    LeaderBoardButton = Button(["./assets/img/Button-a.png",
                    "./assets/img/Button-b.png"], 0, 0, -50, LeaderBoard, "Leaderboard", SmallFont)
    LeaderBoardButton.ResizeSprite(120, 53)
    LeaderBoardButton.CreateHitbox(LeaderBoardButton.imageWidth, LeaderBoardButton.imageHeight)
    Spawnner = Wait(random.uniform(
        0.001, ObstacleMaxWaitBeforeSpawn), SpawnObstacle)
    DifficultyIncrease = Wait(30, IncreaseDifficulty)
    ScoreCounter = Wait(0.1, IncreaseScore)
    SwitchCostume = Wait(0.15, NextCostume)
    Obstacles = []
    score = 0
    MainMenu()
    Backdrop.DrawBackground()
    BigFont.DrawText("Avoid The Obstacle", constants.BLACK,0, 50)
    MediumFont.DrawText("Loading...", constants.BLACK, 0, -10)
    pygame.display.update()
    try:
        HighScore = int(requests.get("https://api.albloh2.repl.co/legacy/db/view/W5CLEFU9WDKS95TP").text)
        Offline = False
    except:
        HighScore = 0
        Offline = True


    def mainloop():
        global Spawnner, Obstacles, run, mode
        clock = pygame.time.Clock()
        run = True
        mode = "MainMenu"
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            if mode == "Game":
                ScoreCounter.check()
                RocketShip.HandlePlayerMovement()
                SwitchCostume.check()
                HandleObstacle()
                ScreenRefresh(mode)
            elif mode == "GameOver":
                MainMenuButton.HandleMouse()
                ScreenRefresh(mode)
            elif mode == "MainMenu":
                PlayButton.HandleMouse()
                LeaderBoardButton.HandleMouse()
                ScreenRefresh(mode)
            elif mode == "Leaderboard":
                MainMenuButton.HandleMouse()
                ScreenRefresh(mode)
            pygame.display.update()
            clock.tick(FPS)
        pygame.mixer.quit()
        pygame.quit()

    mainloop()
except:
    root = tkinter.Tk()
    root.withdraw()
    tkinter.messagebox.showerror("Avoid The Obstacle", f"Uncaught Exception:\n {traceback.format_exc()}")