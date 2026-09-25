    class PortalRecoveryDecision final : public DecisionRule {
    public:
        PortalRecoveryDecision() { require<InsidePortal>(); }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            int move = bot.survival_move();
            if (move < 0) move = bot.best_spread_move(true);
            if (move >= 0)
                return Decision{Execution::SURVIVE, std::string("MOVE ") + DIR[move]};
            if (bot.length >= 4 && bot.units < bot.limit)
                return Decision{Execution::SPLIT, "SPLIT 2"};
            return Decision{Execution::FALLBACK, "MOVE N"};
        }
    };
