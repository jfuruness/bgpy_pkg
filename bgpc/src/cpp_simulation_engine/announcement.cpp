#include <announcement.hpp>


// Constructor
Announcement::Announcement(const std::string& prefix, const std::vector<int>& as_path, int timestamp,
             const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
             const std::optional<int>& roa_origin, Relationships recv_relationship,
             bool withdraw, bool traceback_end,
             const std::vector<std::string>& communities)
    : prefix(prefix), as_path(as_path), timestamp(timestamp),
      seed_asn(seed_asn), roa_valid_length(roa_valid_length), roa_origin(roa_origin),
      recv_relationship(recv_relationship), withdraw(withdraw),
      traceback_end(traceback_end), communities(communities) {}

// Methods
bool Announcement::prefix_path_attributes_eq(const Announcement* ann) const {
    if (!ann) {
        return false;
    }
    return ann->prefix == this->prefix && ann->as_path == this->as_path;
}

bool Announcement::invalid_by_roa() const {
    if (!roa_origin.has_value()) {
        return false;
    }
    return origin() != roa_origin.value() || !roa_valid_length.value();
}

bool Announcement::valid_by_roa() const {
    return roa_origin.has_value() && origin() == roa_origin.value() && roa_valid_length.value();
}

bool Announcement::unknown_by_roa() const {
    return !invalid_by_roa() && !valid_by_roa();
}

bool Announcement::covered_by_roa() const {
    return !unknown_by_roa();
}

bool Announcement::roa_routed() const {
    return roa_origin.has_value() && roa_origin.value() != 0;
}

int Announcement::origin() const {
    if (!as_path.empty()) {
        return as_path.back();
    }
    return -1; // Or another appropriate default value
}
