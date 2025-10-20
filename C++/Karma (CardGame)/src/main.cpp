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
        main_game_loop(starting_player_);
    }

private:
    void change_faceup_cards(){
        int choice;
        int choice_hand;
        int choice_faceup;
        for (int i = 0; i < NUM_PLAYERS; i++)
        {
            while(true){
            cout << "PLAYER " << i + 1 << " Your turn to change a card" << endl;
            show_player_state(i);
            cout << "Do you want to change a card from the hand to the face up cards?" << endl << "1 = yes" << endl << "2 = no" << endl;
            cin >> choice; 
            if (choice == 2)  break;              
                cout << "Enter the index of the card you want to change from your hand " << endl;
                cin >> choice_hand;
                cout << "Enter the index of the card you want to change from your face up cards " << endl;
                cin >> choice_faceup;
                if (choice_hand > 2 || choice_faceup > 2)
                {
                    cout << "Invalid Number" << endl;
                    continue;
                }
                std::swap(players_[i].face_up[choice_faceup],players_[i].hand[choice_hand]);
            };
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
        cout << "=== Player " << (starting_player_ + 1) << " starts ===\n\n";
    }

    void show_player_state(int idx) const {
        const auto& p = players_.at(idx);


        cout << "Face-up:\n";
        for (size_t i = 0; i < p.face_up.size(); ++i) {
            cout << "  [" << i << "] " << p.face_up[i] << '\n';
        }

        cout << "Hand:\n";
        for (size_t i = 0; i < p.hand.size(); ++i) {
            cout << "  [" << i << "] " << p.hand[i] << '\n';
        }

        cout << "\nCards left in deck: " << deck_.size() << "\n\n";
    };

    bool game_over() const { //Function to check if someone has won. 
    for (const auto& p : players_) {
        if (p.hand.empty() && p.face_up.empty() && p.face_down.empty())
            return true; 
    }
    return false;
    }

    int get_rank_value(const std::string& card) const {  // Helper function to get the ranks of the cards because they are originally stored in a string vector.
    std::string rank = card.substr(0, card.find(" of "));

    for (int i = 0; i < (int)ranks_.size(); ++i) {
        if (ranks_[i] == rank)
            return i;  // rank index = rank strength
    }
    return -1; 
    }

    enum class Effect { NONE, RESET, TRANSPARENT, LOWER, BURN };

    Effect get_card_effect(const std::string& card) const {
    std::string rank = card.substr(0, card.find(" of "));

    if (rank == "2")  return Effect::RESET;
    if (rank == "3")  return Effect::TRANSPARENT;
    if (rank == "7")  return Effect::LOWER;   
    if (rank == "10") return Effect::BURN;
    return Effect::NONE;
    }
    enum class Zone { HAND, FACE_UP, FACE_DOWN };

    Zone current_zone(const Player& p) const {
        if (!p.hand.empty())     return Zone::HAND;
        if (!p.face_up.empty())  return Zone::FACE_UP;
        return Zone::FACE_DOWN; 
    }

void main_game_loop(int starting_player) {
    int current_player = starting_player;
    bool must_play_lower_ = false;
    while (!game_over()) {
        cout << "Player: " << current_player << " its your turn !!! " << endl;
        show_player_state(current_player);
        if (!pile_.empty()) {
            cout << "Top of pile: " << pile_.back() << "\n";
        } else {
            cout << "Pile is empty.\n";
        }

        bool blind_draw = false;
        std::vector<std::string>* zone = nullptr; 
        if (!players_[current_player].hand.empty()) {
            zone = &players_[current_player].hand;
            cout << "Play from HAND. ";
        } else if (!players_[current_player].face_up.empty()) {
            zone = &players_[current_player].face_up;
            cout << "Play from FACE-UP. ";
        } else if (!players_[current_player].face_down.empty()) {
            blind_draw = true; 
            cout << "Drawing BLIND from FACE-DOWN...\n";
        } else {
            current_player = (current_player + 1) % NUM_PLAYERS;
            continue;
        }

        std::string played_card;
        int index = -1;

        if (!blind_draw) {
            cout << "Enter index [0.." << (int)zone->size() - 1 << "]: ";
            cin >> index;
            if (index < 0 || index >= static_cast<int>(zone->size())) {
                cout << "Invalid index. Try again.\n";
                continue;
            }
            played_card = (*zone)[index];
        } else {
            auto& fd = players_[current_player].face_down;
            played_card = fd.back();
            fd.pop_back();
            cout << "You revealed: " << played_card << "\n";
        }

        int played_value = get_rank_value(played_card);
        Effect effect    = get_card_effect(played_card);

        bool pile_empty  = pile_.empty();
        int  top_value   = pile_empty ? -1 : get_rank_value(pile_.back());

        bool can_play = false;
        if (effect == Effect::RESET || effect == Effect::TRANSPARENT || pile_empty) {
            can_play = true;
        } else if (must_play_lower_) {
            can_play = (played_value <= top_value);
        } else {
            can_play = (played_value >= top_value);
        }

        if (!can_play) {
            // Illegal -> take pile into HAND; if blind-drew, put the revealed card into HAND too.
            auto& hand = players_[current_player].hand;
            if (!pile_.empty()) {
                hand.insert(hand.end(), pile_.begin(), pile_.end());
                pile_.clear();
            }
            if (blind_draw) {
                hand.push_back(played_card); 
            }
            cout << "Illegal move. You take the pile.\n";
            current_player = (current_player + 1) % NUM_PLAYERS;
            continue;
        }

        // Legal: commit play
        pile_.push_back(played_card);
        if (!blind_draw) {
            zone->erase(zone->begin() + index);
        }

        switch (effect) {
            case Effect::RESET: // 2
                cout << "Pile reset. Any card can follow.\n";
                must_play_lower_ = false;
                break;
            case Effect::TRANSPARENT: // 3
                cout << "Transparent card. Next card sets the bar.\n";
                break;
            case Effect::LOWER: // 7
                cout << "7 played. Next must play LOWER or equal.\n";
                must_play_lower_ = true;
                break;
            case Effect::BURN: // 10
                cout << "10 burns the pile!\n";
                pile_.clear();
                must_play_lower_ = false;
                break;
            default:
                break;
        }

        if (game_over()) {
            cout << "🎉 Player " << (current_player + 1) << " wins the game!\n";
            break;
        }

        current_player = (current_player + 1) % NUM_PLAYERS;
    }
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
