#include <unordered_map>
#include "local_rib.hpp"


LocalRIB::LocalRIB(int max_prefix_block_id) {
    _info.resize(max_prefix_block_id, nullptr);
}

std::shared_ptr<Announcement> LocalRIB::get_ann(const unsigned short int prefix_block_id, const std::shared_ptr<Announcement>& default_ann) const {
    if (prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    return _info[prefix_block_id] ? _info[prefix_block_id] : default_ann;
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
    _info[prefix_block_id] = nullptr;
}

const std::vector<std::shared_ptr<Announcement>>& LocalRIB::prefix_anns() const {
    return _info;
}

void LocalRIB::reset(int max_prefix_block_id_param){
    if (max_prefix_block_id_param != _info.size()){
        // This will happen the first time this gets initialized
        _info.resize(max_prefix_block_id_param, nullptr);
        //throw std::out_of_range("resetting with a different max prefix block id");
    }else{
        std::fill(_info.begin(), _info.end(), nullptr); // Set each element to nullptr
    }
}
