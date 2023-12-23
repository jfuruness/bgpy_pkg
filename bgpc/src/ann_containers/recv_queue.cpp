#include "announcement.hpp"
#include "recv_queue.hpp"

RecvQueue::RecvQueue() {}

void RecvQueue::add_ann(const std::shared_ptr<Announcement>& ann) {
    _info[ann->prefix].push_back(ann);
}

const std::map<std::string, std::vector<std::shared_ptr<Announcement>>>& RecvQueue::prefix_anns() const {
    return _info;
}

const std::vector<std::shared_ptr<Announcement>>& RecvQueue::get_ann_list(const std::string& prefix) const {
    static const std::vector<std::shared_ptr<Announcement>> empty;
    auto it = _info.find(prefix);
    if (it != _info.end()) {
        return it->second;
    }
    return empty;
}
