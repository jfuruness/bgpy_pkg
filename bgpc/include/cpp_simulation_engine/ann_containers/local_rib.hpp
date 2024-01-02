#ifndef LOCAL_RIB_HPP
#define LOCAL_RIB_HPP

#include <memory>
#include <map>
#include <string>
#include <unordered_map>
#include "announcement.hpp"

class LocalRIB {
public:
    LocalRIB(int max_prefix_block_id);

    std::shared_ptr<Announcement> get_ann(const unsigned short int prefix_block_id) const;

    void add_ann(const std::shared_ptr<Announcement>& ann);

    void remove_ann(const unsigned short int prefix_block_id);

    const std::vector<std::shared_ptr<Announcement>>& prefix_anns() const;

    void reset(int max_prefix_block_id);

    std::vector<std::shared_ptr<Announcement>> _info;

};

#endif // LOCAL_RIB_HPP
