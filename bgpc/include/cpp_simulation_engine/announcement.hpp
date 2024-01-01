#ifndef ANNOUNCEMENT_H
#define ANNOUNCEMENT_H

#include <string>
#include <vector>
#include <optional>
#include <memory> // Include for std::shared_ptr
#include <enums.hpp>


class ASPathNode {
public:
    int asn; // ASN attribute as an int
    int as_path_length; // Variable to store the length of the AS path

    std::weak_ptr<ASPathNode> parent;
    std::vector<std::shared_ptr<ASPathNode>> children;

    // Constructor
    explicit ASPathNode(int asn, int as_path_length = 1)
        : asn(asn), as_path_length(as_path_length) {}

    // Other methods...
};


class StaticData {
public:
    const std::string prefix;
    const int timestamp;
    const std::optional<int> seed_asn;
    const std::optional<bool> roa_valid_length;
    const std::optional<int> roa_origin;
    const bool withdraw;
    std::shared_ptr<ASPathNode> path_node; // Shared pointer to ASPathNode

    StaticData(const std::string& prefix, int timestamp, const std::optional<int>& seed_asn,
               const std::optional<bool>& roa_valid_length,
               const std::optional<int>& roa_origin, bool withdraw)
        : prefix(prefix), timestamp(timestamp), seed_asn(seed_asn),
          roa_valid_length(roa_valid_length), roa_origin(roa_origin),
          withdraw(withdraw) {
              if (seed_asn.has_value()) {
                  path_node = std::make_shared<ASPathNode>(seed_asn.value(), 1);
              } else {
                  path_node = nullptr;
                  throw std::runtime_error("seed asn is null");
              }
          }
};


class Announcement {
public:
    unsigned short int prefix_block_id;
    const Relationships recv_relationship;
    const bool traceback_end;
    const std::shared_ptr<StaticData> staticData;
    std::shared_ptr<ASPathNode> as_path_leaf_node;

    // First constructor
    Announcement(unsigned short int prefix_block_id,
                 const std::string& prefix, const std::vector<int>& as_path, int timestamp,
                 const std::optional<int>& seed_asn, const std::optional<bool>& roa_valid_length,
                 const std::optional<int>& roa_origin, Relationships recv_relationship,
                 bool withdraw = false, bool traceback_end = false,
                 const std::vector<std::string>& communities = {});
    // Second constructor
    Announcement(unsigned short int prefix_block_id,
                 std::shared_ptr<StaticData> staticData,
                 Relationships recv_relationship, std::shared_ptr<ASPathNode> as_path_leaf_node,
                 bool traceback_end = false,
                 const std::vector<std::string>& communities = {});

    std::vector<int> as_path() const;
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
