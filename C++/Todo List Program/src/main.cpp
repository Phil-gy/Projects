#include <iostream>
#include <string>
#include <fstream>
#include <limits>
//#include <bits/stdc++.h>
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
            remove_task();
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
        cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // eat leftover '\n'

        for (int i = 1; i <= n; ++i) {
            cout << "Task " << i << ": ";
            std::string task;
            std::getline(cin, task);
            if (task.empty()) {            // prevent blank lines
                cout << "Empty task. Try again.\n";
                --i;
                continue;
            }
            file << task << '\n';
            if (!file) {                   // catch I/O errors immediately
                cout << "Write error. Aborting.\n";
                return;
            }
        }

        cout << n << " task(s) added.\n";
    }


    void remove_task(){

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
        cout << endl << "Enter anything to continue: " << endl;
        string filler;
        cin >> filler;
        cin.clear();

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
