#ifndef ENUMS_H
#define ENUMS_H

enum class Relationships {
    PROVIDERS = 1,
    PEERS = 2,
    CUSTOMERS = 3,
    ORIGIN = 4,
    UNKNOWN = 5
};


enum class Outcomes {
    ATTACKER_SUCCESS = 0,
    VICTIM_SUCCESS = 1,
    DISCONNECTED = 2,
    UNDETERMINED = 3
};


enum class Plane {
    DATA = 0,
    CTRL = 1
};

#endif // ENUMS_H
