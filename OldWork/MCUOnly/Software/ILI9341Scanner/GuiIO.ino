#ifdef MONITOR_CONSOLE

// TODO redo graphics for terminal etc. with more rigerous placement, find out why doing console work crasHES
// at first, crashes when attempting to use FSM library resources

#include "Fsm.h"
#include "USBHost_t36.h"

// User Configurable
const int NUM_LINES = 20;
const uint16_t TEXT_TERMINAL_COLOR = ILI9341_YELLOW; // Color of user input
const uint16_t TEXT_TERMINAL_SENT_COLOR = 0xD3D3D3;
const int FONT_SIZE = 1;

// Objects for USB interaction
USBHost myusb;
USBHub hub1(myusb);
KeyboardController keyboard1(myusb);
bool keyboardActive = false;

// Parametric constants

const int TOP_CORNER = MONITOR_IMAGE_HEIGHT;
const int TEXT_HEIGHT = MONITOR_MAX_HEIGHT - MONITOR_IMAGE_HEIGHT;
const int TEXT_WIDTH = MONITOR_MAX_WIDTH;

String TEXT_BUFFERS[NUM_LINES] = {""};
uint16_t COLOR_BUFFERS[NUM_LINES] = {0};
String TEXT_TERMINAL = "";

// FSM for commands, current commands are "ENABLE", "RESET", "LIST"

#define STATE_INACTIVE_KEYPRESS 1
//State state_inactive(&state_inactive_enter, NULL, &state_inactive_exit); // inactive mode is when the monitor runs and the terminal is off
//State state_inactive(NULL, NULL, NULL); 

#define STATE_MENU_INIT_RESET 2
#define STATE_MENU_INIT_ENABLE 3
#define STATE_MENU_INIT_LIST 4
//State state_menu(state_menu_enter, state_menu_run, NULL); // Menu manages portal between mod options and running mode

/*
#define STATE_PARAMETERCHANGE_SUCCESS 5
#define STATE_PARAMETERCHANGE_FAILURE 6
#define STATE_PARAMETERCHANGE_BACK 7
#define STATE_PARAMETERCHANGE_EXIT 8
#define STATE_PARAMETERCHANGE_SLOWFREQ 9
#define STATE_PARAMETERCHANGE_SLOWAMP 10
#define STATE_PARAMETERCHANGE_FASTFREQ 11
#define STATE_PARAMETERCHANGE_FASTAMP 12
*/
//State state_parameterChange_menu(state_parameterChange_menu_enter, NULL, NULL);
//State state_parameterChange_slowFrequency(&state_parameterChange_slowFrequency_enter, &state_parameterChange_slowFrequency_run, &state_parameterChange_slowFrequency_exit);
//State state_parameterChange_slowAmplitude(&state_parameterChange_slowAmplitude_enter, &state_parameterChange_slowAmplitude_run, &state_parameterChange_slowAmplitude_exit);
//State state_parameterChange_fastFrequency(&state_parameterChange_fastFrequency_enter, &state_parameterChange_fastFrequency_run, &state_parameterChange_fastFrequency_exit);
//State state_parameterChange_fastAmplitude(&state_parameterChange_fastAmplitude_enter, &state_parameterChange_fastAmplitude_run, &state_parameterChange_fastAmplitude_exit);

//Fsm fsm(state_inactive);

/*
 * This function creates all of the connections between states for the terminal inputs
 */
void setupFSM() {
  // Menu transitions
  //fsm.add_transition(&state_inactive, &state_menu, STATE_INACTIVE_KEYPRESS, NULL);
  //fsm.add_transition(&state_menu, &state_inactive, STATE_MENU_INIT_ENABLE, NULL);
  //fsm.add_transition(&state_menu, &state_parameterChange_menu, STATE_MENU_INIT_RESET, NULL);  */
  // State change menu transitions
  /*
  fsm.addState(&state_parameterChange_menu, &state_menu, STATE_PARAMETERCHANGE_EXIT, NULL);
  fsm.addState(&state_parameterChange_menu, &state_parameterChange_slowFrequency, STATE_PARAMETERCHANGE_SLOWFREQUENCY, NULL);
  fsm.addState(&state_parameterChange_menu, &state_parameterChange_slowAmplitude, STATE_PARAMETERCHANGE_SLOWAMPLITUDE, NULL);
  fsm.addState(&state_parameterChange_menu, &state_parameterChange_fastFrequency, STATE_PARAMETERCHANGE_FASTFREQUENCY, NULL);
  fsm.addState(&state_parameterChange_menu, &state_parameterChange_fastAmplitude, STATE_PARAMETERCHANGE_FASTAMPLITUDE, NULL);
  */
}
void state_inactive_enter() {
  restartOutput();
  keyboardActive = false;
  addNewLine("Outputs enabled", ILI9341_ORANGE);
}

void state_inactive_exit() {
  haltOutput();
  keyboardActive = true;
  addNewLine("Outputs disabled", ILI9341_ORANGE);
}

void state_menu_enter() {
  addNewLine("Enter a command, type \"LIST\" for info.", ILI9341_WHITE);
}

void state_menu_run() {
  TEXT_TERMINAL = "";
  if(TEXT_TERMINAL == (String) "LIST") { // Lists all commands
    addNewLine("List of all commands: ", ILI9341_GREEN);
    addNewLine("ENABLE -> leaves menu and goes back to monitor", ILI9341_BLUE);
    addNewLine("RESET -> enters menu for changing scanning properties", ILI9341_BLUE);
  } else if(TEXT_TERMINAL == (String) "ENABLE") { // Goes back to idle
    //fsm.trigger(STATE_MENU_INIT_ENABLE);
  } else if(TEXT_TERMINAL == (String) "RESET") { // Modifies parameters
    //fsm.trigger(STATE_MENU_INIT_RESET);
  } else {
    addNewLine("Unrecognized request", ILI9341_ORANGE);
  }
}

/*
void state_parameterChange_initial_enter() {
  addNewLine("Specify new scope parameters:", ILI9341_WHITE);
}

void state_parameterChange_slowFrequency_enter() {
  addNewLine("Specify slow frequency: ", ILI9341_WHITE); 
}

void state_parameterChange_slowFrequency_update() {
  float newFrequency = TEXT_TERMINAL.toFloat();
  if(newFrequency) {
    addNewLine("New slow frequency: " + newFrequency, ILI9341_GREEN);
    fsm.
  } else {
    addNewLine("Invalid format, please retry.");
  }
}
*/

/*
 * Determines which command to initialize
 */

/*
 * Sets up peripherals and the monitor
 */
void setupGUI() {
  // Initializes monitor
  //addNewLine("Monitor Initialized", ILI9341_GREEN);
  
  // Initializes keyboard
  myusb.begin();
  keyboard1.attachPress(OnPress);
  setupFSM();
  //addNewLine("USB Initialized", ILI9341_GREEN);
}

/*
 * Updates the console messages currently on display and updates the FSM
 */
void drawTextBuffer() {
  tft.setTextSize(FONT_SIZE);
  if(monitorActive) {
    tft.fillRect(0, TOP_CORNER, TEXT_WIDTH, TEXT_HEIGHT, ILI9341_BLACK);
  } else {
    tft.fillRect(0, 0, MONITOR_MAX_WIDTH, MONITOR_MAX_HEIGHT, ILI9341_BLACK);
  }
  for(int index = 0; index < NUM_LINES;index++) {
    int newTopCorner = ((NUM_LINES - 1) - index) * ((MONITOR_MAX_HEIGHT - 15) / NUM_LINES);
    tft.setCursor(0, newTopCorner);
    if(!monitorActive || newTopCorner >= TOP_CORNER) {
      tft.setTextColor(COLOR_BUFFERS[index]);
      tft.println(TEXT_BUFFERS[index]);
    }
  }
  // Prints layer between user input and terminal
  tft.fillRect(0, MONITOR_MAX_HEIGHT - 20, TEXT_WIDTH, 3, ILI9341_WHITE);
  
  // Prints current user text
  tft.setCursor(0, MONITOR_MAX_HEIGHT - 12);
  if(keyboardActive) {
    tft.setTextColor(TEXT_TERMINAL_COLOR);
  } else {
    tft.setTextColor(ILI9341_MAGENTA);
  }
  tft.println("-> " + TEXT_TERMINAL);
}

/*
 * Adds a new line by shifting back all of the old ones
 */
void addNewLine(String message, uint16_t color) {
  for(int index = NUM_LINES - 1; index > 0; index--) {
    TEXT_BUFFERS[index] = TEXT_BUFFERS[index - 1];
  }
  TEXT_BUFFERS[0] = message;

  for(int index = NUM_LINES - 1; index > 0; index--) {
    COLOR_BUFFERS[index] = COLOR_BUFFERS[index - 1];
  }
  COLOR_BUFFERS[0] = color;
  drawTextBuffer(); // Refreshes
}

/*
 * Recieves a single key from the attached USB device
 */
void OnPress(int key) {
  //fsm.trigger(STATE_INACTIVE_KEYPRESS);
  if(key == 127) { // Might be a backspace
    TEXT_TERMINAL.remove(TEXT_TERMINAL.length() - 1);
  } else if(key == 10) { // Might be enter, lets finite state machine do its job with current input and arbitrate console status
    //fsm.run_machine();
  } else { // Otherwise is probably a character
    TEXT_TERMINAL.concat((char) key);
  }
  drawTextBuffer();
}
#endif
