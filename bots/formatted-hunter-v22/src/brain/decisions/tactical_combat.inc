    class TacticalCombatDecision final : public DecisionRule {
    public:
        TacticalCombatDecision() {
            require<OutsidePortal>();
            require<NotGrowing>();
            require<HasMinimumForce>();
        }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            std::string route = bot.boost_surround_action();
            if (!route.empty()) return Decision{Execution::SURROUND, "MOVE " + route};
            route = bot.boost_trap_action();
            if (!route.empty()) return Decision{Execution::TRAP, "MOVE " + route};
            return std::nullopt;
        }
    };
