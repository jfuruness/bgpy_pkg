#ifndef ANNOUNCEMENT_H
#define ANNOUNCEMENT_H

#include <string>
#include <vector>
#include <optional>
#include <relationships.h>

class Announcement {
public:
    const std::string prefix;
    const std::vector<int> as_path;
    const int timestamp;
    const std::optional<int> seed_asn;
    const std::optional<bool> roa_valid_length;
    const std::optional<int> roa_origin;
    const Relationships recv_relationship;
    const bool withdraw;
    const bool traceback_end;
    const std::vector<std::string> communities;

    Announcement(const std::string& prefix, const std::vector<int>& as_path, int timestamp,
                 const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
                 const std::optional<int>& roa_origin, Relationships recv_relationship,
                 bool withdraw = false, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});

    bool prefix_path_attributes_eq(const Announcement* ann) const;
    bool invalid_by_roa() const;
    bool valid_by_roa() const;
    bool unknown_by_roa() const;
    bool covered_by_roa() const;
    bool roa_routed() const;
    int origin() const;
};

#endif // ANNOUNCEMENT_H
