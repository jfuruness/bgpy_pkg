#ifndef ANNOUNCEMENT_H
#define ANNOUNCEMENT_H

#include <string>
#include <vector>
#include <optional>
#include <memory> // Include for std::shared_ptr
#include <enums.hpp>

#include <boost/container/small_vector.hpp> // Include Boost's small_vector


class StaticData {
public:
    const std::string prefix;
    const int timestamp;
    const std::optional<int> seed_asn;
    const std::optional<bool> roa_valid_length;
    const std::optional<int> roa_origin;
    const bool withdraw;

    StaticData(const std::string& prefix, int timestamp, const std::optional<int>& seed_asn,
               const std::optional<bool>& roa_valid_length,
               const std::optional<int>& roa_origin, bool withdraw)
        : prefix(prefix), timestamp(timestamp), seed_asn(seed_asn),
          roa_valid_length(roa_valid_length), roa_origin(roa_origin),
          withdraw(withdraw) {}
};


class Announcement {

public:
    // To be compatible with python, can't be const
    unsigned short int prefix_block_id;
    const Relationships recv_relationship;
    const bool traceback_end;
    //const std::vector<int> as_path;
    boost::container::small_vector<int, 6> as_path; // Changed to small_vector
    //const std::vector<std::string> communities;
    const std::shared_ptr<StaticData> staticData;


    Announcement(unsigned short int prefix_block_id,
                 const std::string& prefix, const boost::container::small_vector<int, 6>& as_path, int timestamp,
                 const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
                 const std::optional<int>& roa_origin, Relationships recv_relationship,
                 bool withdraw = false, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});

    // New constructor
    Announcement(unsigned short int prefix_block_id,
                 std::shared_ptr<StaticData> staticData, const boost::container::small_vector<int, 6>& as_path,
                 Relationships recv_relationship, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});


    Announcement(const unsigned short int prefix_block_id,
                 const std::string& prefix,
                 const std::vector<int>& as_path,
                 int timestamp,
                 const std::optional<int>& seed_asn = std::nullopt,
                 const std::optional<bool>& roa_valid_length = std::nullopt,
                 const std::optional<int>& roa_origin = std::nullopt,
                 Relationships recv_relationship = Relationships::UNKNOWN,
                 bool withdraw = false,
                 bool traceback_end = false,
                 const std::vector<std::string>& communities = std::vector<std::string>());

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
