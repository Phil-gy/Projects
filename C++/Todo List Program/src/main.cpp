#include <iostream>
#include <string>
#include <fstream>
#include <limits>
#include <cstdio>
using std::cout, std::cin, std::endl, std::fstream, std::ofstream, std::string;

class todo_list{
    const std::string filename = "todolist.txt";
    public:
    void action(int choice){
        switch (choice)
        {
        case 1:
            add_task();
            break;
        case 2:
            int n;
            view_tasks();
            cout << "Which task do you want to remove ? " << endl;
            cin >> n;
            remove_task(n);
            break;
        case 3:
            view_tasks();
            break;
        case 4: 
            cout << "Goodbye" << endl;
            break;
        default:
            break;
        }
    }

    void add_task() { 
        std::ofstream file(filename, std::ios::app); 
        if (!file) {
            cout << "Error: can't open " << filename << " for writing.\n";
            return;
        }

        cout << "How many tasks do you want to add? ";
        int n;
        if (!(cin >> n) || n <= 0) {
            cout << "Invalid number.\n";
            cin.clear();
            cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            return;
        }
        cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); 

        for (int i = 1; i <= n; ++i) {
            cout << "Task " << i << ": ";
            std::string task;
            std::getline(cin, task);
            if (task.empty()) {           
                cout << "Empty task. Try again.\n";
                --i;
                continue;
            }
            file << task << '\n';
            if (!file) {                   
                cout << "Write error. Aborting.\n";
                return;
            }
        }

        cout << n << " task(s) added.\n";
    }


    bool remove_task(int n) {
        std::ifstream in(filename);
        if (!in) return false;

        std::ofstream out("todolist.tmp");
        if (!out) return false;

        std::string line;
        int idx = 0;
        bool removed = false;
        while (std::getline(in, line)) {
            ++idx;
            if (idx == n) { removed = true; continue; }
            out << line << '\n';
        }
        in.close();
        out.close();

        if (!removed) { std::remove("todolist.tmp"); return false; }

        std::remove(filename.c_str());
        std::rename("todolist.tmp", filename.c_str());
        return true;
    }

    void view_tasks(){
        std::ifstream ReadFile("todolist.txt");
        if (!ReadFile)
        {
            cout << "No Tasks yet added" << endl;
            return;
        }
        std::string line;
        int i = 0;
        cout << endl << "All Tasks: " << endl;
        while (std::getline(ReadFile, line))
        {
            if (line.empty()) continue;
            cout << ++i << ". " << line << '\n';
        }
    }


};


int main() {
    int choice;
    todo_list tl;
    do
    {
        cout << "---- Todo List ----" << endl;
        cout << "Choose your action: " << endl;
        cout << "1. Add Task" << endl;
        cout << "2. Remove task" << endl;
        cout << "3. Show all tasks" << endl;
        cout << "4. Exit App" << endl;
        cin >> choice;

        tl.action(choice);
    } while (choice != 4);
    
}
