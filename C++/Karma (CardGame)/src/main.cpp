#include <algorithm>
#include <iostream>
#include <random>
#include <string>
#include <vector>

using std::cout, std::cin, std::endl, std::string, std::vector;

static constexpr int NUM_PLAYERS         = 3;
static constexpr int START_FACE_DOWN     = 3;
static constexpr int START_FACE_UP       = 3;
static constexpr int START_HAND_CARDS    = 3;

struct Player {
    vector<string> hand;      // active hand (starts at 3 after setup)
    vector<string> face_up;   // 3 visible cards
    vector<string> face_down; // 3 hidden
};

class KarmaGame {
    const vector<string> suits_ { "Clubs", "Diamonds", "Hearts", "Spades" };
    const vector<string> ranks_ { "2","3","4","5","6","7","8","9","10","J","Q","K","A" };

    vector<Player> players_;
    vector<string> deck_;
    vector<string> pile_;
    int starting_player_ = 0;

    std::mt19937 rng_{ std::random_device{}() };

public:
    KarmaGame() : players_(NUM_PLAYERS) {
        build_deck();
        shuffle_deck();
    }

    void setup_and_start() {
        deal_initial();
        change_faceup_cards();
        choose_starting_player();
        show_player_state(starting_player_);
        // main_game_loop(); // hook up later
    }

private:
    void change_faceup_cards(){
        int choice;
        int choice_hand;
        int choice_faceup;
        for (int i = 0; i < NUM_PLAYERS; i++)
        {
            do{
            cout << "PLAYER " << i + 1 << " Your turn to change a card" << endl;
            show_player_state(i);
            cout << "Do you want to change a card from the hand to the face up cards?" << endl << "1 = yes" << endl << "2 = no" << endl;
            cin >> choice; 
            if (choice == 1)
            {
                do
                {                
                cout << "Enter the index of the card you want to change from your hand " << endl;
                cin >> choice_hand;
                cout << "Enter the index of the card you want to change from your face up cards " << endl;
                cin >> choice_faceup;
                if (choice_hand > 2 || choice_faceup > 2)
                {
                    cout << "Invalid Number" << endl;
                }
                }while (choice_hand > 2 || choice_faceup > 2);
                std::swap(players_[i].face_up[choice_faceup],players_[i].face_down[choice_hand]);
            }
            } while (choice != 2);
        }
        


    }
    void build_deck() {
        deck_.clear();
        deck_.reserve(suits_.size() * ranks_.size());
        for (const auto& s : suits_) {
            for (const auto& r : ranks_) {
                deck_.push_back(r + " of " + s);
            }
        }
    }

    void shuffle_deck() {
        std::shuffle(deck_.begin(), deck_.end(), rng_);
    }

    // Draws one card from the back (top) of the deck.
    string draw_one() {
        if (deck_.empty()) {
            throw std::runtime_error("Deck exhausted while dealing.");
        }
        string c = deck_.back();
        deck_.pop_back();
        return c;
    }

    void deal_initial() {
        // Clear any prior state
        for (auto& p : players_) {
            p.hand.clear();
            p.face_up.clear();
            p.face_down.clear();
        }
        pile_.clear();

        // Ensure deck has enough cards for initial deal
        const int needed = NUM_PLAYERS * (START_FACE_DOWN + START_FACE_UP + START_HAND_CARDS);
        if ((int)deck_.size() < needed) {
            throw std::runtime_error("Not enough cards to deal initial setup.");
        }

        // Deal 3 face-down to each player
        for (int i = 0; i < START_FACE_DOWN; ++i) {
            for (auto& p : players_) {
                p.face_down.push_back(draw_one());
            }
        }
        // Deal 3 face-up to each player
        for (int i = 0; i < START_FACE_UP; ++i) {
            for (auto& p : players_) {
                p.face_up.push_back(draw_one());
            }
        }
        // Deal 3 hand cards to each player
        for (int i = 0; i < START_HAND_CARDS; ++i) {
            for (auto& p : players_) {
                p.hand.push_back(draw_one());
            }
        }
    }

    void choose_starting_player() {
        std::uniform_int_distribution<int> dist(0, NUM_PLAYERS - 1);
        starting_player_ = dist(rng_);
    }

    void show_player_state(int idx) const {
        const auto& p = players_.at(idx);
      //  cout << "=== Player " << (idx + 1) << " starts ===\n\n";

        cout << "Face-down (hidden): " << p.face_down.size() << " cards\n";
        // (Don’t reveal contents; shown here only for debugging: comment out in real game)
        // for (size_t i = 0; i < p.face_down.size(); ++i) cout << "  [?]\n";

        cout << "Face-up:\n";
        for (size_t i = 0; i < p.face_up.size(); ++i) {
            cout << "  [" << i << "] " << p.face_up[i] << '\n';
        }

        cout << "Hand:\n";
        for (size_t i = 0; i < p.hand.size(); ++i) {
            cout << "  [" << i << "] " << p.hand[i] << '\n';
        }

        cout << "\nCards left in deck: " << deck_.size() << "\n\n";
    }
};

int main() {
    try {
        KarmaGame game;
        game.setup_and_start();
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << endl;
        return 1;
    }
    return 0;
}
