#include <stdio.h>
#include "rc-switch/RCSwitch.h"
#include <vector>
#include <algorithm>
#include <iterator>
#include <iostream>

bool containsSwitch(int number, std::vector<int>& vector); 
void pushBackSwitch(int number, std::vector<int>& vector);

int main(int argc, char *argv[]) {
    std::vector<int> activeSwitches = std::vector<int>();
    int PIN = 2; // this is pin 13, aka GPIO22 on the PI3, see https://www.element14.com/community/servlet/JiveServlet/previewBody/73950-102-10-339300/pi3_gpio.png

    if (wiringPiSetup () == -1) {
        printf("ERROR: WiringPi not installed. Make sure you have WiringPi installed.\n");
        printf("Quick tutorial:\n\n");
        printf("    sudo apt-get install git\n");
        printf("    cd ~/\n");
        printf("    git clone git://git.drogon.net/wiringPi\n");
        printf("    cd wiringPi\n");
        printf("    ./build\n\n");
        return 1;
    }

    // put the PIN into no-pull/up down state:
    // see https://github.com/ninjablocks/433Utils/issues/21
    pullUpDnControl(PIN, PUD_OFF);

    RCSwitch mySwitch = RCSwitch();

    mySwitch.enableReceive(PIN);

    printf("Listening\n");

    while(true) {

        if (mySwitch.available()) {
            
            int value = mySwitch.getReceivedValue();
            
            if (value == 0) {
                printf("Unknown encoding\n");
            } else {
                //printf("Received %lu / %i bit Protocol: %i\n", mySwitch.getReceivedValue(), mySwitch.getReceivedBitlength(), mySwitch.getReceivedProtocol());
                printf("%lu 1\n", mySwitch.getReceivedValue());
                pushBackSwitch(mySwitch.getReceivedValue(), activeSwitches);
            }

            mySwitch.resetAvailable();
        } else { 
	  for(auto pos : activeSwitches) {
	    printf("%lu 0\n", pos);
            activeSwitches.erase(std::remove_if(activeSwitches.begin(), activeSwitches.end(), [pos](int i){return pos==i;}));
	  }
	}

	std::cout.flush();
        delay(100);
    }
}

bool containsSwitch(int number, std::vector<int>& v) {
  if(std::find(v.begin(), v.end(), number) != v.end()) {
    return true;
  }
  return false;
}

void pushBackSwitch(int number, std::vector<int>& vector) {
  if(!containsSwitch(number, vector))
    vector.push_back(number);
}
