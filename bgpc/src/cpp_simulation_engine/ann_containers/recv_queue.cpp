#include "announcement.hpp"
#include "recv_queue.hpp"

RecvQueue::RecvQueue(int max_prefix_block_id) : _info(max_prefix_block_id) {
    // _info is initialized with max_prefix_block_id empty vectors
    _info.resize(max_prefix_block_id); // Resizing the vector to hold max_prefix_block_id empty vectors
}

void RecvQueue::add_ann(const std::shared_ptr<Announcement>& ann) {
    if (ann->prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    _info[ann->prefix_block_id].push_back(ann);
}

const std::vector<std::vector<std::shared_ptr<Announcement>>>& RecvQueue::prefix_anns() const {
    return _info;
}

const std::vector<std::shared_ptr<Announcement>>& RecvQueue::get_ann_list(const unsigned short int prefix_block_id) const {
    if (prefix_block_id >= _info.size()) {
        throw std::out_of_range("Prefix block ID is out of range");
    }
    return _info[prefix_block_id];
}

void RecvQueue::reset(int max_prefix_block_id_param){
    if (max_prefix_block_id_param != _info.size()){
        // This will happen the first time this gets initialized

        _info.resize(max_prefix_block_id_param); // Resizing the vector to hold max_prefix_block_id empty vectors
        //throw std::out_of_range("resetting with a different max prefix block id");
    }
    for (auto& ann_list : _info) {
        ann_list.clear(); // Clear each list in the vector
    }
}
