
import os

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')

def list_tools():
    tools = []
    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if fname.endswith('.py') and not fname.startswith('__'):
            tools.append(fname)
    return tools

def show_menu(tools):
    print("=== AI Music Assistant - Dynamic Tool Launcher ===")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")
    print("0. Exit")

def main():
    tools = list_tools()
    while True:
        show_menu(tools)
        choice = input("\nSelect a tool to run (0 to exit): ").strip()
        if choice == '0':
            print("Goodbye!")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(tools):
            script = tools[int(choice) - 1]
            script_path = os.path.join(SCRIPTS_DIR, script)
            print(f"Running: {script}")
            os.system(f'python "{script_path}"')
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
