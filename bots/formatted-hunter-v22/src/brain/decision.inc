    // Small rule framework modelled after prototype13's decision objects.
    // Requirements are mandatory; fire-on conditions are optional triggers.
    class DecisionRule {
    public:
        virtual ~DecisionRule() = default;

        std::optional<Decision> evaluate(Bot& bot) const {
            for (Condition condition : requirements_)
                if (!condition(bot)) return std::nullopt;
            if (!triggers_.empty()) {
                bool fired = false;
                for (Condition condition : triggers_) fired |= condition(bot);
                if (!fired) return std::nullopt;
            }
            return choose(bot);
        }

    protected:
        using Condition = bool (*)(const Bot&);

        template<class Predicate> void require() {
            requirements_.push_back([](const Bot& bot) { return Predicate{}(bot); });
        }
        template<class Predicate> void fire_on() {
            triggers_.push_back([](const Bot& bot) { return Predicate{}(bot); });
        }
        virtual std::optional<Decision> choose(Bot& bot) const = 0;

    private:
        std::vector<Condition> requirements_;
        std::vector<Condition> triggers_;
    };

    struct OutsidePortal {
        bool operator()(const Bot& bot) const { return !bot.inside; }
    };
    struct InsidePortal {
        bool operator()(const Bot& bot) const { return bot.inside; }
    };
    struct NotGrowing {
        bool operator()(const Bot& bot) const { return !bot.should_focus_growth(); }
    };
    struct Growing {
        bool operator()(const Bot& bot) const { return bot.should_focus_growth(); }
    };
    struct HasMinimumForce {
        bool operator()(const Bot& bot) const { return bot.units >= 3; }
    };
    struct AskedToMove {
        bool operator()(const Bot& bot) const { return bot.asked_to_move; }
    };
    struct CanSplit {
        bool operator()(const Bot& bot) const {
            return bot.length >= 4 && bot.units < bot.limit;
        }
    };
    struct SignallingFriend {
        bool operator()(const Bot& bot) const { return bot.current_signal; }
    };
