#ifndef ANNOUNCEMENT_H
#define ANNOUNCEMENT_H

#include <string>
#include <vector>
#include <optional>
#include <memory> // Include for std::shared_ptr
#include <enums.hpp>


class StaticData {
public:
    const unsigned short int prefix_block_id;
    const std::string prefix;
    const int timestamp;
    const std::optional<int> seed_asn;
    const std::optional<bool> roa_valid_length;
    const std::optional<int> roa_origin;
    const bool withdraw;

    StaticData(const unsigned short int prefix_block_id, const std::string& prefix, int timestamp, const std::optional<int>& seed_asn,
               const std::optional<bool>& roa_valid_length,
               const std::optional<int>& roa_origin, bool withdraw)
        : prefix_block_id(prefix_block_id), prefix(prefix), timestamp(timestamp), seed_asn(seed_asn),
          roa_valid_length(roa_valid_length), roa_origin(roa_origin),
          withdraw(withdraw) {}
};


class Announcement {

public:
    // To be compatible with python, can't be const
    //unsigned short int prefix_block_id;
    const std::shared_ptr<StaticData> staticData;
    const std::vector<int> as_path;
    const Relationships recv_relationship;
    //const bool traceback_end;
    //const std::vector<std::string> communities;


    Announcement(unsigned short int prefix_block_id,
                 const std::string& prefix, const std::vector<int>& as_path, int timestamp,
                 const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
                 const std::optional<int>& roa_origin, Relationships recv_relationship,
                 bool withdraw = false, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});

    // New constructor
    Announcement(unsigned short int prefix_block_id,
                 std::shared_ptr<StaticData> staticData, const std::vector<int>& as_path,
                 Relationships recv_relationship, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});

    unsigned short int prefix_block_id() const {
        return staticData->prefix_block_id;
    }
    std::string prefix() const;
    int timestamp() const;
    std::optional<int> seed_asn() const;
    std::optional<bool> roa_valid_length() const;
    std::optional<int> roa_origin() const;
    bool withdraw() const;

    bool operator==(const Announcement& other) const;

    bool prefix_path_attributes_eq(const Announcement* ann) const;
    bool invalid_by_roa() const;
    bool valid_by_roa() const;
    bool unknown_by_roa() const;
    bool covered_by_roa() const;
    bool roa_routed() const;
    int origin() const;
};

#endif // ANNOUNCEMENT_H
