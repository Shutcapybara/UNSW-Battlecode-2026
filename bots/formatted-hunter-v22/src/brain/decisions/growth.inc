    class GrowthDecision final : public DecisionRule {
    public:
        GrowthDecision() { require<Growing>(); }
    private:
        std::optional<Decision> choose(Bot& bot) const override {
            return Decision{Execution::GROW, bot.growth_action()};
        }
    };
