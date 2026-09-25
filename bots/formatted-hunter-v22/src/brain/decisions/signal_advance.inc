    class SignalAdvanceDecision final : public DecisionRule {
    public:
        SignalAdvanceDecision() { fire_on<SignallingFriend>(); }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            if (bot.destination(bot.head, bot.facing) < 0) return std::nullopt;
            return Decision{Execution::ADVANCE, std::string("MOVE ") + DIR[bot.facing]};
        }
    };
