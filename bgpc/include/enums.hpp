#ifndef ENUMS_H
#define ENUMS_H

enum class Relationships: unsigned char {
    PROVIDERS = 1,
    PEERS = 2,
    CUSTOMERS = 3,
    ORIGIN = 4,
    UNKNOWN = 5
};


enum class Outcomes: unsigned char {
    ATTACKER_SUCCESS = 0,
    VICTIM_SUCCESS = 1,
    DISCONNECTED = 2,
    UNDETERMINED = 3
};


enum class Plane: unsigned char {
    DATA = 0,
    CTRL = 1
};

#endif // ENUMS_H
