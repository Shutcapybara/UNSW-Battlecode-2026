    class PortalTripDecision final : public DecisionRule {
        std::optional<Decision> choose(Bot& bot) const override {
            std::string command = bot.portal_action();
            if (command.empty()) return std::nullopt;
            return Decision{Execution::PORTAL_TRIP, command};
        }
    };
