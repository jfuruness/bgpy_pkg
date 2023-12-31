#include <unordered_map>
#include "local_rib.hpp"

LocalRIB::LocalRIB(int max_prefix_block_id) {
    _info.reserve(max_prefix_block_id);
}

std::shared_ptr<Announcement> LocalRIB::get_ann(const unsigned short int prefix_block_id, const std::shared_ptr<Announcement>& default_ann) const {
    auto it = _info.find(prefix_block_id);
    if (it != _info.end()) {
        return it->second;
    }
    return default_ann;
}

void LocalRIB::add_ann(const std::shared_ptr<Announcement>& ann) {
    _info[ann->prefix_block_id] = ann;
}

void LocalRIB::remove_ann(const unsigned short int prefix_block_id) {
    _info.erase(prefix_block_id);
}

const std::unordered_map<unsigned short int, std::shared_ptr<Announcement>>& LocalRIB::prefix_anns() const {
    return _info;
}
