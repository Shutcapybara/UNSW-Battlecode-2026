    class MoveAsideDecision final : public DecisionRule {
    public:
        MoveAsideDecision() { fire_on<AskedToMove>(); }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            int move = bot.best_spread_move(true);
            if (move < 0) return std::nullopt;
            return Decision{Execution::YIELD, std::string("MOVE ") + DIR[move]};
        }
    };
