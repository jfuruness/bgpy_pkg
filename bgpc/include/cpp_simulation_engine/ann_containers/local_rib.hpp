#ifndef LOCAL_RIB_HPP
#define LOCAL_RIB_HPP

#include <memory>
#include <map>
#include <string>
#include "announcement.hpp"

class LocalRIB {
public:
    LocalRIB();

    std::shared_ptr<Announcement> get_ann(const std::string& prefix, const std::shared_ptr<Announcement>& default_ann = nullptr) const;

    void add_ann(const std::shared_ptr<Announcement>& ann);

    void remove_ann(const std::string& prefix);

    const std::map<std::string, std::shared_ptr<Announcement>>& prefix_anns() const;

protected:
    std::map<std::string, std::shared_ptr<Announcement>> _info;
};

#endif // LOCAL_RIB_HPP
