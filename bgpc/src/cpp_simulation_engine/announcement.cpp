#include <announcement.hpp>


// Constructor
/*
Announcement::Announcement(const std::string& prefix, const std::vector<int>& as_path, int timestamp,
             const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
             const std::optional<int>& roa_origin, Relationships recv_relationship,
             bool withdraw, bool traceback_end,
             const std::vector<std::string>& communities)
    : prefix(prefix), as_path(as_path), timestamp(timestamp),
      seed_asn(seed_asn), roa_valid_length(roa_valid_length), roa_origin(roa_origin),
      recv_relationship(recv_relationship), withdraw(withdraw),
      traceback_end(traceback_end), communities(communities) {}
*/

Announcement::Announcement(
             unsigned short int prefix_block_id,
             const std::string& prefix, const std::vector<int>& as_path, int timestamp,
             const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
             const std::optional<int>& roa_origin, Relationships recv_relationship,
             bool withdraw, bool traceback_end, const std::vector<std::string>& communities)
    : as_path(as_path),
      staticData(std::make_shared<StaticData>(prefix_block_id, prefix, timestamp, seed_asn, roa_valid_length, roa_origin, withdraw)),
      recv_relationship(recv_relationship) {}
      //communities(communities) {}



Announcement::Announcement(unsigned short int prefix_block_id,
                           std::shared_ptr<StaticData> staticData, const std::vector<int>& as_path,
                           Relationships recv_relationship, bool traceback_end,
                           const std::vector<std::string>& communities)
    : staticData(staticData), as_path(as_path),
      recv_relationship(recv_relationship) {}
      //communities(communities) {}



std::string Announcement::prefix() const {
    return staticData->prefix;
}

int Announcement::timestamp() const {
    return staticData->timestamp;
}

std::optional<int> Announcement::seed_asn() const {
    return staticData->seed_asn;
}

std::optional<bool> Announcement::roa_valid_length() const {
    return staticData->roa_valid_length;
}

std::optional<int> Announcement::roa_origin() const {
    return staticData->roa_origin;
}

bool Announcement::withdraw() const {
    return staticData->withdraw;
}


// Equality comparison operator
bool Announcement::operator==(const Announcement& other) const {
    return prefix_block_id() == other.prefix_block_id()
        && as_path == other.as_path
        && timestamp() == other.timestamp()
        && seed_asn() == other.seed_asn()
        && roa_valid_length() == other.roa_valid_length()
        && roa_origin() == other.roa_origin()
        && recv_relationship == other.recv_relationship
        && withdraw() == other.withdraw();
        //&& traceback_end == other.traceback_end;
        //&& communities == other.communities;
}

// Methods
bool Announcement::prefix_path_attributes_eq(const Announcement* ann) const {
    if (!ann) {
        return false;
    }
    return ann->prefix() == prefix() && ann->as_path == as_path;
}

bool Announcement::invalid_by_roa() const {
    if (!roa_origin().has_value()) {
        return false;
    }
    return origin() != roa_origin().value() || !roa_valid_length().value();
}

bool Announcement::valid_by_roa() const {
    return roa_origin().has_value() && origin() == roa_origin().value() && roa_valid_length().value();
}

bool Announcement::unknown_by_roa() const {
    return !invalid_by_roa() && !valid_by_roa();
}

bool Announcement::covered_by_roa() const {
    return !unknown_by_roa();
}

bool Announcement::roa_routed() const {
    return roa_origin().has_value() && roa_origin().value() != 0;
}

int Announcement::origin() const {
    if (!as_path.empty()) {
        return as_path.back();
    }
    return -1; // Or another appropriate default value
}
