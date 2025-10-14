#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <cstdlib>
#include <ctime>
#define NUM_PLAYERS 3
#define STARTING_CARDS 3
using std::cout, std::endl, std::cin;

struct Player {
    std::vector<std::string> hand;      // active hand (starts at 3 after setup)
    std::vector<std::string> face_up;   // 3 chosen visible cards
    std::vector<std::string> face_down; // 3 hidden
};

std::vector<Player> players_;   // size = NUM_PLAYERS
std::vector<std::string> pile_; // the central stack

class karma {
    const std::vector<std::string> suits = { "Clubs", "Diamonds", "Hearts", "Spades" };
    const std::vector<std::string> ranks = { "2", "3", "4", "5", "6", "7", "8", "9",
                                             "10", "J", "Q", "K", "A" };
    std::vector<std::string> deck_;                 // the live deck
    std::vector<std::vector<std::string>> hands_;   // size = NUM_PLAYERS, each player’s cards

    public:
    karma() {
        hands_.assign(NUM_PLAYERS, {});   
    };

    void give_starting_cards() {
       deck_.clear();
       hands_.assign(NUM_PLAYERS, {});
        for (const auto& suit : suits) {
            for (const auto& rank : ranks) {
                deck_.push_back(rank + " of " + suit);
            }
    }
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(deck_.begin(), deck_.end(), g);

    for (int p = 0; p < NUM_PLAYERS; ++p) {
    for (int i = 0; i < STARTING_CARDS; ++i) {
        hands_[p].push_back(deck_.back());
        deck_.pop_back();
    }
}
    }
    int starting_player_ = 0; 

    void determine_starting_player() {
        static std::mt19937 g(std::random_device{}());
        std::uniform_int_distribution<int> dist(0, NUM_PLAYERS - 1);
        starting_player_ = dist(g);
        main_game_loop(starting_player_);
    }

    int amount_of_cards = STARTING_CARDS;

    void main_game_loop(int starting_player) {
        int current = starting_player;
        int choice;
        // show current player's hand
        int sp = starting_player;
        std::cout << "Player " << (sp + 1) << " hand:\n";
        for (int i = 0; i < (int)hands_[sp].size(); ++i)
            std::cout << "  [" << i << "] " << hands_[sp][i] << "\n";

        int idx;
        std::cout << "Choose a card index: ";
        std::cin >> idx;
        if (idx < 0 || idx >= (int)hands_[sp].size()) {
            std::cout << "Invalid index.\n";
            return; // or re-prompt
        }
        // cout << "What card do you want to set ? " << endl;
        // cin >> choice;
        // if (choice )
        // {
        //     /* code */
        // }
        
        
    }

};

int main() {
    karma game;
    game.give_starting_cards();
    game.determine_starting_player();
    return 0;
}
