#include "local_rib.hpp"

LocalRIB::LocalRIB() {}

std::shared_ptr<Announcement> LocalRIB::get_ann(const std::string& prefix, const std::shared_ptr<Announcement>& default_ann) const {
    auto it = _info.find(prefix);
    if (it != _info.end()) {
        return it->second;
    }
    return default_ann;
}

void LocalRIB::add_ann(const std::shared_ptr<Announcement>& ann) {
    _info[ann->prefix] = ann;
}

void LocalRIB::remove_ann(const std::string& prefix) {
    _info.erase(prefix);
}

const std::map<std::string, std::shared_ptr<Announcement>>& LocalRIB::prefix_anns() const {
    return _info;
}
