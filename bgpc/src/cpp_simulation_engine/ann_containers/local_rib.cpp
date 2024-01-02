#include <unordered_map>
#include "local_rib.hpp"


LocalRIB::LocalRIB(int max_prefix_block_id) {
    _info.resize(max_prefix_block_id);
    for (int i = 0; i < max_prefix_block_id; ++i) {
        // For each element in the vector, assign a new shared_ptr to a default Announcement
        _info[i] = std::make_shared<Announcement>(static_cast<unsigned short int>(i));
    }
}

std::shared_ptr<Announcement> LocalRIB::get_ann(const unsigned short int prefix_block_id) const {
    if (prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    return _info[prefix_block_id];
}

void LocalRIB::add_ann(const std::shared_ptr<Announcement>& ann) {
    if (ann->prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    _info[ann->prefix_block_id] = ann;
}

void LocalRIB::remove_ann(const unsigned short int prefix_block_id) {
    if (prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    _info[prefix_block_id] = std::make_shared<Announcement>(prefix_block_id);
}

const std::vector<std::shared_ptr<Announcement>>& LocalRIB::prefix_anns() const {
    return _info;
}

void LocalRIB::reset(int max_prefix_block_id_param){
    if (max_prefix_block_id_param != _info.size()){
        // This will happen the first time this gets initialized
        _info.resize(max_prefix_block_id_param);
        //throw std::out_of_range("resetting with a different max prefix block id");
    }

    for (int i = 0; i < max_prefix_block_id_param; ++i) {
        // For each element in the vector, assign a new shared_ptr to a default Announcement
        _info[i] = std::make_shared<Announcement>(static_cast<unsigned short int>(i));
    }
}
