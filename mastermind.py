#!/usr/bin/env python3
#
#   Simple Mastermind (TM - Hasbro) Implementation
#
#   @author Aaron S. Crandall <crandall@gonzaga.edu>
#   @copyright 2022
#

from random import randrange
from time import sleep
from colorama import Fore, Back, Style, init

# colorama has an init() to set the terminal up
#  this only matters for Windows systems
init()


def cls():
    """ Simple clear screen function """
    print("\n" * 80)


# ** ******************************************************
class Peg:
    """ Base class for all peg tokens in the game """

    def __init__(self) -> None:
        self.symbol = "\u2B24"
        self.background = Back.LIGHTCYAN_EX
        self.termUnicode = "X"
        self.colorName = None

    def __str__(self):
        return self.termUnicode

    def __eq__(self, other):
        return self.colorName == other.colorName

    @staticmethod
    def getPeg(pegChar: str) -> "Peg":
        """ Static factory method to create Pegs by character name """
        if pegChar == "R":
            return RedPeg()
        elif pegChar == "U":
            return BluePeg()
        elif pegChar == "G":
            return GreenPeg()
        elif pegChar == "B":
            return BlackPeg()
        elif pegChar == "W":
            return WhitePeg()
        elif pegChar == "Y":
            return YellowPeg()
        else:
            return None


class RedPeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "Red"
        self.termUnicode = Fore.RED + self.symbol


class BluePeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "Blue"
        self.termUnicode = Fore.BLUE + self.symbol


class GreenPeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "Green"
        self.termUnicode = Fore.GREEN + self.symbol


class YellowPeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "Yellow"
        self.termUnicode = Fore.YELLOW + self.symbol


class BlackPeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "Black"
        self.termUnicode = Fore.BLACK + self.symbol


class WhitePeg(Peg):
    def __init__(self) -> None:
        super().__init__()
        self.colorName = "White"
        self.termUnicode = Fore.WHITE + self.symbol


# ** *************************************************************************
class TargetPegs:
    def __init__(self, pegs=None) -> None:
        self.revealPegs = False
        if pegs:
            self.pegs = pegs
        else:
            self.pegs = []
            for i in range(4):
                self.pegs.append(self.getRandomPeg())

    def setRevealPegs(self):
        self.revealPegs = True

    def setHidePegs(self):
        self.revealPegs = False

    def getRandomPeg(self):
        pegLetters = ["R", "U", "G", "Y", "B", "W"]
        return Peg.getPeg(pegLetters[randrange(len(pegLetters))])

    def __str__(self):
        ret = ""
        if self.revealPegs:
            for peg in self.pegs:
                ret += str(peg) + " "
        else:
            ret += "-SECRET-"
        ret += "  |"
        ret += Fore.WHITE
        return ret


# ** *************************************************************************
HINT_SYMBOL = "\u25C6"


class RightColorWrongPlace:
    def __init__(self) -> None:
        self.termUnicode = Fore.WHITE + HINT_SYMBOL

    def __str__(self) -> str:
        return self.termUnicode


class RightColorRightPlace:
    def __init__(self) -> None:
        self.termUnicode = Fore.BLACK + HINT_SYMBOL

    def __str__(self) -> str:
        return self.termUnicode


# ** *************************************************************************
class Guess:
    """ A player's guess line on the board """

    def __init__(self, pegs: list = None, number: int = 0):
        if pegs:
            self.pegs = pegs
        else:
            self.pegs = []

        self.number = number
        self.hints = []

    def setPegs(self, pegs: list) -> None:
        self.pegs = pegs

    def isCorrect(self) -> bool:
        if len(self.hints) != len(self.pegs):
            return False
        for hint in self.hints:
            if isinstance(hint, RightColorWrongPlace):
                return False
        return True

    def calcHints(self, targetPegsContainer: TargetPegs) -> None:
        targetPegs = targetPegsContainer.pegs  # bad practice

        targetTaken = [False, False, False, False]
        guessIsUsed = [False, False, False, False]

        # Find Right Color, Right Location
        for i in range(len(self.pegs)):
            if self.pegs[i] == targetPegs[i]:
                self.hints.append(RightColorRightPlace())
                targetTaken[i] = True
                guessIsUsed[i] = True

        # Fine Remaining Colors, Wrong Location
        for i in range(len(self.pegs)):
            currGuessPeg = self.pegs[i]
            if not guessIsUsed[i]:
                for j in range(len(self.pegs)):
                    if not targetTaken[j] and currGuessPeg == targetPegs[j]:
                        self.hints.append(RightColorWrongPlace())
                        targetTaken[j] = True
                        break  # Check next peg guess

    def __str__(self) -> str:
        ret = f"{self.number:02} |  "
        if len(self.pegs) > 0:
            for peg in self.pegs:
                ret += f"{peg} "
        else:
            ret += " " * 8
        ret += Fore.WHITE + "  |  "
        for hint in self.hints:
            ret += f"{hint} "
        ret += Fore.WHITE
        return ret


# ** *************************************************************************
class Mastermind:
    """ A game of Mastermind """

    def __init__(self):
        self.targetPegs = TargetPegs()
        self.guesses = []
        self.totalGuesses = 12
        self.isDone = False

        for i in range(self.totalGuesses):
            self.guesses.append(Guess(number=(self.totalGuesses - i)))

        self.calculateSecretAnimation()

    def calculateSecretAnimation(self):
        print("Calculating my secret... it'll be tough!")
        for i in range(5):
            for j in range(3):
                print(".", end="", flush=True)
                sleep(0.25)

            print("\r      \r", end="")
        print("Got it! Let's go.")
        sleep(2)

    def playRound(self):
        """
        Plays a round of Mastermind (max 12 guesses)
        """
        print("Starting mastermind!")
        print("\n" * 3)
        # Add animation & awesome here
        print(self)

        currGuessNum = 1
        while not self.isDone:
            guessPegs = self.getPlayerGuess()
            currGuess = self.guesses[-1 * currGuessNum]
            currGuess.setPegs(guessPegs)
            currGuess.calcHints(self.targetPegs)
            currGuessNum += 1

            # See if it's a win or out of guesses
            if currGuess.isCorrect():
                self.targetPegs.setRevealPegs()
                print(self)
                print("You Won!!!!")
                self.isDone = True
            elif currGuessNum > self.totalGuesses:
                self.targetPegs.setRevealPegs()
                print(self)
                self.isDone = True
                print("Too bad -- Try again")
            else:
                print(self)

    def getPlayerGuess(self) -> list:
        """
        Get a player's guess from terminal
        @return List of Pegs (none if error)
        """
        newPegs = False

        while not newPegs:
            print(
                f"{Fore.RED}(R)ed{Fore.WHITE} -- {Fore.BLUE}bl(U)e{Fore.WHITE} -- {Fore.GREEN}(G)reen{Fore.WHITE}"
            )
            print(
                f"{Fore.YELLOW}(Y)ellow{Fore.WHITE} -- {Fore.BLACK}(B)lack{Fore.WHITE} -- (W)hite"
            )
            print("Example input: RYBU for Red Yellow Black blUe")
            userInput = input("Enter your guess: ").strip().upper()
            if userInput == "SHOW":
                self.targetPegs.setRevealPegs()
            newPegs = self.getPegsFromGuess(userInput)
        return newPegs

    def getPegsFromGuess(self, userInput: str) -> list:
        """
        Decode a string of Pegs (user input)
        @param userInput: string of uppercase Peg characters
        @return list of Peg objects (none if error)
        """
        ret = []
        for ch in userInput:
            newPeg = Peg.getPeg(ch)
            if not newPeg:
                print(f"{ch} -- invalid color, try again")
                return None
            else:
                ret.append(newPeg)
        return ret

    def __str__(self) -> str:
        ret = ""
        ret += f"{'*'*28}\n"
        ret += f"   |  {str(self.targetPegs)}\n"
        ret += f"{'*'*28}\n"

        for guess in self.guesses:
            ret += str(guess) + "\n"

        return ret


# ** *************************************************************************
if __name__ == "__main__":
    print("Starting game - it's time for Mastermind.")
    print(Style.RESET_ALL)

    game = Mastermind()

    try:
        game.playRound()
    except KeyboardInterrupt:
        print("\nQutting")

    print("Done.")
