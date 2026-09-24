#pragma once
#include "world.h"
#include <limits>

struct Snake { int id; bool ours,alive=true; vector<int> body; };
struct State {
    vector<Snake> snakes;
    vector<std::pair<int,bool>> food;
    vector<int> removed;
    int actor=0, clock=0, next_id=1000000000;
    double external=0;
};
struct Action { std::string path; bool split=false; int head=0,len=0,depth=0,risk=0; double value=-1e30; };

struct Planner {
    World &w;
    vector<double> potential,danger;
    vector<int> fixed, beds;
    std::map<int,vector<int>> observed;
    int opponent=-1, nodes=0;
    bool changed=false;
    explicit Planner(World &world):w(world),potential(w.n,0),danger(w.n,0),fixed(w.n,-1) {}

    bool grower(int id) const {
        return (uint32_t(id)*2654435761u)%P::anchor_stride==0;
    }
    double worth(int length,bool ours) const {
        double life=P::life_value*(w.round<350?1.0:0.35);
        double bank=w.round>250?P::bank_value*(w.round-250)/250.0*length*length:0;
        return (P::material_value*length+life+bank)*(ours?1:P::kill_weight);
    }
    // Only reconstruct enemies whose complete tail is observable. Incomplete
    // dragons stay fixed obstacles/threats; no invented length or tail release.
    vector<int> complete_body(int head) const {
        int id=w.parts[head].id;vector<int> body={head};
        while(true) {
            int prev=-1;
            for(int c:observed.at(id))if(!w.contains(body,c)&&w.next(c,w.parts[c].facing)==body.back()) {prev=c;break;}
            if(prev<0)break;
            body.push_back(prev);
        }
        if(body.size()!=observed.at(id).size()||body.size()<2)return {};
        int tail=body.back();
        for(int d=0;d<4;d++) {
            int v=w.next(tail,d),edge=w.edges[w.key(tail,d)];
            if(edge==-2||(edge>=0&&v<0)||(v>=0&&w.tiles[v].seen!=w.round))return {};
        }
        return body;
    }
    State model() {
        observed.clear();beds.clear();opponent=-1;nodes=0;
        std::fill(potential.begin(),potential.end(),0);std::fill(danger.begin(),danger.end(),0);
        std::fill(fixed.begin(),fixed.end(),-1);
        State s;s.snakes.push_back({w.id,true,true,w.body});
        for(int c=0;c<w.n;c++)if(w.parts[c].id>=0)observed[w.parts[c].id].push_back(c);
        // Terrain distance, including occupied destinations, for duel selection.
        vector<int> ds(w.n,-1),q={w.head};ds[w.head]=0;
        for(size_t i=0;i<q.size();i++)if(ds[q[i]]<P::duel_range)
            for(int v:w.graph[q[i]])if(v>=0&&ds[v]<0){ds[v]=ds[q[i]]+1;q.push_back(v);}
        int closest=P::duel_range+1;vector<int> enemy;
        for(int c:w.enemy_heads)if(ds[c]>=0&&ds[c]<closest) {
            auto b=complete_body(c);if(!b.empty()){opponent=w.parts[c].id;closest=ds[c];enemy=b;}
        }
        if(opponent>=0)s.snakes.push_back({opponent,false,true,enemy});
        for(int c=0;c<w.n;c++) {
            auto p=w.parts[c];
            if(p.id>=0&&p.id!=opponent&&(p.id!=w.id||!w.contains(w.body,c)))fixed[c]=p.id;
            if(w.tiles[c].bed&&w.tiles[c].due>w.round)beds.push_back(c);
        }
        for(int head:w.enemy_heads)if(w.parts[head].id!=opponent) {
            vector<int> reach(w.n,-1),todo={head};reach[head]=0;
            for(size_t i=0;i<todo.size();i++)if(reach[todo[i]]<2)
                for(int v:w.graph[todo[i]])if(v>=0&&reach[v]<0&&
                    (w.parts[v].id<0||w.parts[v].id==w.id)) {
                    reach[v]=reach[todo[i]]+1;danger[v]=std::max(danger[v],reach[v]==1?1.0:0.3);todo.push_back(v);
                }
        }
        auto dist=w.distances(w.head);
        vector<int> claims(w.n,100000);
        for(int head:w.ally_heads){auto a=w.distances(head,10);for(int c=0;c<w.n;c++)if(a[c]>=0)claims[c]=std::min(claims[c],a[c]);}
        vector<vector<int>> reverse(w.n);
        for(int c=0;c<w.n;c++)for(int v:w.graph[c])if(v>=0)reverse[v].push_back(c);
        std::priority_queue<std::pair<double,int>> queue;
        for(int c=0;c<w.n;c++)if(dist[c]>=0) {
            double v=0;
            if(w.food(c,dist[c],6)) {
                int wait=w.confirmed(c)?0:std::max(0,w.tiles[c].due-w.round-dist[c]);
                v=12-0.6*wait;if(claims[c]<dist[c])v-=5;
            }
            for(int d=0;d<4;d++)if(w.graph[c][d]==-2)v=std::max(v,4.0);
            if(v>0){potential[c]=v;queue.push({v,c});}
        }
        while(!queue.empty()) {
            auto [value,c]=queue.top();queue.pop();if(value!=potential[c])continue;
            for(int prev:reverse[c])if(fixed[prev]<0&&value-1>potential[prev]) {
                potential[prev]=value-1;queue.push({value-1,prev});
            }
        }
        return s;
    }
    int occupant(const State&s,int cell) const {
        for(size_t i=0;i<s.snakes.size();i++)if(s.snakes[i].alive&&w.contains(s.snakes[i].body,cell))return i;
        return -1;
    }
    bool static_block(const State&s,int cell) const {
        return fixed[cell]>=0&&!w.contains(s.removed,fixed[cell]);
    }
    bool pearl(const State&s,int cell) const {
        for(auto it=s.food.rbegin();it!=s.food.rend();++it)if(it->first==cell)return it->second;
        return w.confirmed(cell);
    }
    void kill(State&s,int index) const {
        auto &a=s.snakes[index];if(!a.alive)return;
        for(size_t i=0;i<a.body.size();i+=2)s.food.push_back({a.body[i],true});
        a.alive=false;
    }
    void advance(State&s,int old_id) const {
        int next=-1;
        for(size_t i=0;i<s.snakes.size();i++)if(s.snakes[i].alive&&s.snakes[i].id>old_id&&
            (next<0||s.snakes[i].id<s.snakes[next].id))next=i;
        if(next<0) {
            for(size_t i=0;i<s.snakes.size();i++)if(s.snakes[i].alive&&
                (next<0||s.snakes[i].id<s.snakes[next].id))next=i;
            s.clock++;
            for(int c:beds)if(w.tiles[c].due==w.round+s.clock&&!pearl(s,c)&&occupant(s,c)<0&&!static_block(s,c))s.food.push_back({c,true});
        }
        s.actor=next;
    }
    bool split_allowed(const State&s,int index) const {
        const auto&a=s.snakes[index];int len=a.body.size();
        if(len<4||w.round+s.clock>=P::split_stop)return false;
        if(a.ours&&(w.units>=w.limit||int(w.body.size())!=w.length))return false;
        if(a.ours&&grower(a.id)&&w.round+s.clock>=P::anchor_start&&len>=P::anchor_length)return false;
        int extra=0;for(auto&b:s.snakes)if(b.alive&&b.ours==a.ours&&b.id>=1000000000)extra++;
        return extra<2&&(!a.ours||w.units+extra<w.limit);
    }
    bool apply(State&s,const Action&a) const {
        int index=s.actor;if(index<0)return false;
        int id=s.snakes[index].id;
        if(a.split) {
            if(!split_allowed(s,index))return false;
            auto &p=s.snakes[index];int n=p.body.size();
            Snake child{s.next_id++,p.ours,true,{p.body[n-1],p.body[n-2]}};
            p.body.resize(n-2);s.snakes.push_back(child);advance(s,id);return true;
        }
        for(size_t k=0;k<a.path.size();k++) {
            auto &p=s.snakes[index];
            if(k&&p.body.size()<=2)return false;
            int c=w.next(p.body[0],std::string(DIRS).find(a.path[k]));
            if(c<0||w.contains(p.body,c))return false;
            int other=occupant(s,c);
            if(other>=0) {
                if(s.snakes[other].body[0]!=c)return false;
                kill(s,other);kill(s,index);advance(s,id);return true;
            }
            if(static_block(s,c)) {
                if(!w.parts[c].head)return false;
                int victim=fixed[c];bool ours=w.parts[c].ours;
                s.external+=(ours?-1:1)*worth(observed.at(victim).size(),ours);
                s.removed.push_back(victim);
                // Only observed body segments are known; no guessed carcass food.
                kill(s,index);advance(s,id);return true;
            }
            bool food=pearl(s,c);p.body.insert(p.body.begin(),c);
            if(food)s.food.push_back({c,false});else p.body.pop_back();
            if(k)p.body.pop_back();
        }
        advance(s,id);return true;
    }
    int exits(const State&s,const Snake&a) const {
        int n=0;
        for(int d=0;d<4;d++){int c=w.next(a.body[0],d);if(c>=0&&occupant(s,c)<0&&!static_block(s,c))n++;}
        return n;
    }
    double evaluate(const State&s) const {
        double value=s.external;int us=0;
        for(const auto&a:s.snakes)if(a.alive) {
            double sign=a.ours?1:-1;
            value+=sign*(worth(a.body.size(),a.ours)+P::mobility_value*exits(s,a));
            if(a.ours) {
                us++;int h=a.body[0];
                value+=P::target_value*potential[h]-P::visit_cost*std::min(20,w.tiles[h].visits)-P::outside_risk*danger[h];
            }
        }
        if(!us&&w.units==1)value-=1000;
        return value;
    }
    vector<std::pair<double,std::pair<Action,State>>> moves(const State&s) const {
        vector<std::pair<double,std::pair<Action,State>>> out;
        auto add=[&](Action a){State next=s;if(apply(next,a))out.push_back({evaluate(next),{a,std::move(next)}});};
        if(s.actor<0)return out;
        for(char d:std::string(DIRS)) {
            Action a;a.path=std::string(1,d);add(a);
            if(P::sprint_max>=2)for(char e:std::string(DIRS)) {
                a.path=std::string(1,d)+e;add(a);
                if(P::sprint_max>=3)for(char f:std::string(DIRS)){a.path=std::string(1,d)+e+f;add(a);}
            }
        }
        if(split_allowed(s,s.actor)){Action a;a.split=true;add(a);}
        return out;
    }
    double search(const State&s,int depth,int&budget,double alpha,double beta) {
        nodes++;if(budget--<=0||depth==0||s.actor<0)return evaluate(s);
        bool maximize=s.snakes[s.actor].ours;
        auto options=moves(s);
        if(options.empty()) {auto dead=s;int id=dead.snakes[dead.actor].id;kill(dead,dead.actor);advance(dead,id);return evaluate(dead);}
        std::stable_sort(options.begin(),options.end(),[&](const auto&a,const auto&b){return maximize?a.first>b.first:a.first<b.first;});
        double value=maximize?-1e30:1e30;
        int count=0;
        for(const auto&option:options) {
            if(count++>=P::reply_width)break;
            double next=search(option.second.second,depth-1,budget,alpha,beta);
            value=maximize?std::max(value,next):std::min(value,next);
            if(maximize)alpha=std::max(alpha,value);else beta=std::min(beta,value);
            if(beta<=alpha||budget<=0)break;
        }
        return value;
    }
    Action decide() {
        auto initial=model();auto options=moves(initial);Action best;
        Action greedy;
        for(const auto &option:options)if(option.first>greedy.value){greedy=option.second.first;greedy.value=option.first;}
        int allowance=std::max(1,P::node_budget/std::max(1,int(options.size())));
        for(const auto &option:options) {
            auto candidate=option.second.first;const auto&state=option.second.second;
            int budget=allowance;
            double value=(opponent>=0&&P::reply_plies>0)?search(state,P::reply_plies,budget,-1e30,1e30):option.first;
            // Equal per-root budgets avoid privileging the first compass direction.
            if(value>best.value){best=candidate;best.value=value;}
        }
        if(options.empty())best.path="N";
        changed=best.path!=greedy.path||best.split!=greedy.split;
        best.head=w.head;best.len=w.length-(best.split?2:0);best.depth=nodes;
        if(!best.split)for(char d:best.path){int c=w.next(best.head,std::string(DIRS).find(d));if(c<0)break;best.head=c;}
        return best;
    }
};
