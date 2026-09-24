#pragma once
#include "world.h"
struct Node {
    vector<int> body,eaten;
    double reward=0,rank=0;
};
struct Action {std::string path;bool split=false;int head=0,len=0;double value=-1e30;int depth=0,risk=9;};
struct Planner {
    World &w;
    vector<double> danger,potential;
    vector<int> source,claims;
    explicit Planner(World &world):w(world),danger(w.n,0),potential(w.n,0),source(w.n,-1),claims(w.n,100000) {}
    void model() {
        for(int origin:w.enemy_heads) {
            vector<int> ds(w.n,-1),q={origin};ds[origin]=0;
            for(size_t i=0;i<q.size();i++) {
                int c=q[i];if(ds[c]>=3)continue;
                for(int v:w.graph[c])if(v>=0&&ds[v]<0&&
                        (w.parts[v].id<0||w.parts[v].id==w.id)) {
                    int dep=ds[v]=ds[c]+1;
                    danger[v]=std::max(danger[v],dep==1?1.0:dep==2?.35:.12);q.push_back(v);
                }
            }
        }
        // Only one packet kind, one consumer: soft food ownership.
        auto allies=w.reports;
        for(int c:w.ally_heads)allies[w.parts[c].id]={c,2,w.round};
        for(auto [id,r]:allies)if(w.round-r.round<=4) {
            auto ds=w.distances(r.cell,12);
            for(int c=0;c<w.n;c++)if(ds[c]>=0)claims[c]=std::min(claims[c],ds[c]);
        }
        auto ds=w.distances(w.head);
        vector<vector<int>> reverse(w.n);
        for(int c=0;c<w.n;c++)for(int v:w.graph[c])if(v>=0)reverse[v].push_back(c);
        std::priority_queue<std::pair<double,int>> q;
        for(int c=0;c<w.n;c++) {
            if(ds[c]<0)continue;
            double value=0;
            if(w.food(c,ds[c])) {
                value=P::pearl_value*(w.confirmed(c)?1.0:0.65);
                if(claims[c]+1<ds[c])value*=P::claim_discount;
            }
            for(int d=0;d<4;d++)if(w.graph[c][d]==-2) {value=std::max(value,P::frontier_value);break;}
            if(value>0) {potential[c]=value;source[c]=c;q.push({value,c});}
        }
        while(!q.empty()) {
            auto [v,c]=q.top();q.pop();if(v!=potential[c])continue;
            for(int prev:reverse[c]) {
                if(w.parts[prev].id>=0&&w.parts[prev].id!=w.id)continue;
                double next=v-P::step_cost;
                if(next>potential[prev]) {potential[prev]=next;source[prev]=source[c];q.push({next,prev});}
            }
        }
    }
    bool step(Node &node,int d,int future,int sprint_index=0) const {
        if(sprint_index&&node.body.size()<=2)return false; // pay before growth
        int dest=w.next(node.body[0],d,future>0);
        if(dest<0||w.blocked(dest,node.body))return false; // before tail vacates
        bool eaten=w.contains(node.eaten,dest);
        bool pearl=!eaten&&(future==0?w.confirmed(dest):w.food(dest,future+1));
        node.body.insert(node.body.begin(),dest);
        if(!pearl)node.body.pop_back();
        if(sprint_index)node.body.pop_back();
        if(pearl)node.eaten.push_back(dest);
        double discount=std::pow(P::future_discount,future);
        node.reward+=discount*(P::pearl_value*(int(pearl)-int(sprint_index>0))-
            P::risk_cost*danger[dest]*(future?0.3:1.0)-P::visit_cost*std::min(20,w.tiles[dest].visits));
        if(future&&w.tiles[dest].seen<0)node.reward-=0.3*discount;
        return true;
    }
    double rank(const Node &n,int turn) const {
        int c=n.body[0];double end=potential[c];
        if(w.contains(n.eaten,source[c]))end=0;
        int exits=0;for(int d=0;d<4;d++){int v=w.next(c,d,true);exits+=v>=0&&!w.blocked(v,n.body);}
        return n.reward+std::pow(P::future_discount,turn)*end+0.2*exits;
    }
    Action plan(const std::string &path) const {
        Node start;start.body=w.body;Action out;out.path=path;
        for(size_t i=0;i<path.size();i++)if(!step(start,std::string(DIRS).find(path[i]),0,i))return out;
        out.head=start.body[0];out.len=start.body.size();
        out.risk=danger[out.head]>=1?2:danger[out.head]>0?1:0;
        out.depth=1;out.value=rank(start,1);
        vector<Node> beam={start};
        for(int turn=1;turn<P::horizon;turn++) {
            vector<Node> next;
            for(const auto &node:beam)for(int d=0;d<4;d++) {
                Node child=node;if(!step(child,d,turn))continue;
                child.rank=rank(child,turn+1);next.push_back(std::move(child));
            }
            if(next.empty())break;
            std::stable_sort(next.begin(),next.end(),[](const Node&a,const Node&b){return a.rank>b.rank;});
            // Diverse leaves: at most two histories per destination.
            vector<Node> kept;std::map<int,int> per_cell;
            for(auto &n:next)if(per_cell[n.body[0]]++<2) {
                kept.push_back(std::move(n));if((int)kept.size()>=P::beam)break;
            }
            beam=std::move(kept);out.depth=turn+1;out.value=beam[0].rank;
        }
        return out;
    }
    vector<int> catchment(int root,const vector<int>&body,const vector<int>&other_body) const {
        vector<int> q={root},ds(w.n,-1),food;ds[root]=0;
        for(size_t i=0;i<q.size();i++) {
            int c=q[i];if(ds[c]>=P::fork_radius)continue;
            for(int v:w.graph[c])if(v>=0&&ds[v]<0&&!w.blocked(v,body)&&!w.contains(other_body,v)) {
                ds[v]=ds[c]+1;q.push_back(v);
                if(w.food(v,ds[v],P::fork_window))food.push_back(v);
            }
        }
        return food;
    }
    bool fork() const {
        if(w.length<P::split_min||w.length>=P::reserve_len||w.round>=P::split_stop||
           w.units>=std::min(w.limit,P::population_max)||(int)w.body.size()!=w.length)return false;
        if(danger[w.head]>=0.35)return false;
        vector<int> parent(w.body.begin(),w.body.end()-2);
        vector<int> child={w.body.back(),w.body[w.body.size()-2]};
        int exits=0;
        for(int v:w.graph[child[0]])if(v>=0&&!w.blocked(v,child)&&!w.contains(parent,v)&&danger[v]<1)exits++;
        if(!exits)return false;
        exits=0;
        for(int v:w.graph[parent[0]])if(v>=0&&!w.blocked(v,parent)&&!w.contains(child,v))exits++;
        if(!exits)return false;
        if(!P::fork_food)return true;
        auto pf=catchment(parent[0],parent,child),cf=catchment(child[0],child,parent);
        for(int a:pf)for(int b:cf)if(a!=b)return true;
        return false;
    }
    Action decide() {
        model();Action best;
        auto better=[](const Action&a,const Action&b) {
            // Survival precedes utility; all scores are from separate bounded beams.
            bool a_full=a.depth>=P::horizon,b_full=b.depth>=P::horizon;
            if(a_full!=b_full)return a_full;
            if(a.risk!=b.risk)return a.risk<b.risk;
            if(a.depth!=b.depth)return a.depth>b.depth;
            return a.value>b.value;
        };
        for(int d=0;d<4;d++) {
            std::string one(1,DIRS[d]);auto a=plan(one);if(better(a,best))best=a;
            if(P::sprint_max>=2)for(int e=0;e<4;e++) {
                auto b=plan(one+DIRS[e]);if(better(b,best))best=b;
                if(P::sprint_max>=3)for(int f=0;f<4;f++) {
                    auto c=plan(one+DIRS[e]+DIRS[f]);if(better(c,best))best=c;
                }
            }
        }
        if(fork()&&(best.depth>=P::horizon||best.depth==0)) {
            best.split=true;best.path.clear();best.head=w.head;best.len=w.length-2;
        }
        if(best.depth==0&&!best.split) {
            // No planned continuation: prefer a visible enemy head over a wall.
            for(int d=0;d<4;d++) {int c=w.next(w.head,d);if(c>=0&&w.parts[c].head&&!w.parts[c].ours) {
                best.path=std::string(1,DIRS[d]);best.head=c;best.len=w.length;return best;
            }}
            best.path="N";best.head=w.head;best.len=w.length;
        }
        return best;
    }
};
