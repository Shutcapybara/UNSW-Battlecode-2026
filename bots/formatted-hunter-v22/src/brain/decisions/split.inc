    class SplitDecision final : public DecisionRule {
    public:
        SplitDecision() { require<CanSplit>(); }
    private:
        std::optional<Decision> choose(Bot&) const override {
            return Decision{Execution::SPLIT, "SPLIT 2"};
        }
    };
