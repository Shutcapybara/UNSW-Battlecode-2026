    class AttackDecision final : public DecisionRule {
    public:
        AttackDecision() { require<HasMinimumForce>(); }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            std::string route = bot.attack_path();
            if (route.empty()) return std::nullopt;
            int steps = std::min<int>(static_cast<int>(route.size()), bot.length - 1);
            if (steps <= 0) return std::nullopt;
            return Decision{Execution::ATTACK, "MOVE " + route.substr(0, steps)};
        }
    };
