# Karma (cardGame)

An implementation of the card game **Karma** written in **C++**.
The rules of the game:
♠️ Karma – Game Rules Summary

Karma is a fast-paced shedding card game where the goal is to be the first player to get rid of all your cards.

🎯 Objective

Be the first player to play all your cards — from hand, face-up, and finally face-down piles.

🃏 Setup

Each player receives:

3 face-down cards (hidden; can’t look at them)

3 face-up cards (visible to everyone)

3 cards in hand

The rest of the deck becomes the draw pile.

A random player starts, and turns go clockwise.

🔁 Game Flow

Players start with their hand cards.

On your turn, you must play a card equal to or higher in value than the top card of the pile.

Played cards go on the center pile (pile_).

If you can’t play a valid card,
→ you must pick up the entire pile and add it to your hand.

When your hand is empty:

You start playing from your face-up cards.

Once those are gone, you play blindly from your face-down cards (no peeking).

If you play an illegal face-down card,
→ you must take the pile (including that revealed card) into your hand.  



🏆 Winning

The first player to clear all cards (hand → face-up → face-down) wins.
The last player left holding cards is the “Karma” (loser).

---

## Features
 

---

## Compilation & Usage

### Windows (MinGW or MSYS2)
```bash
g++ src/main.cpp -o todo
./todo
