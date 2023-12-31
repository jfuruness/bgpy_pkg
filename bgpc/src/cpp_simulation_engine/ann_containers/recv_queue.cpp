#include "announcement.hpp"
#include "recv_queue.hpp"

RecvQueue::RecvQueue(int max_prefix_block_id) {
   if(max_prefix_block_id > 4){
        _info.reserve(max_prefix_block_id);
   }
}

void RecvQueue::add_ann(const std::shared_ptr<Announcement>& ann) {
    _info[ann->prefix_block_id].push_back(ann);
}

const std::unordered_map<unsigned short int, std::vector<std::shared_ptr<Announcement>>>& RecvQueue::prefix_anns() const {
    return _info;
}

const std::vector<std::shared_ptr<Announcement>>& RecvQueue::get_ann_list(const unsigned short int prefix_block_id) const {
    static const std::vector<std::shared_ptr<Announcement>> empty;
    auto it = _info.find(prefix_block_id);
    if (it != _info.end()) {
        return it->second;
    }
    return empty;
}
