#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>
#include "params.h"
using std::vector;
constexpr char DIRS[] = "NESW";
struct Part { int id=-1; bool ours=false, head=false; int facing=0; };
struct Tile { int seen=-1000, pearl=-1000, due=-1000, visits=0; bool bed=false; };
struct World {
    int id=0,w=0,h=0,n=0,limit=64,round=0,length=3,units=1,head=0;
    char team='A';
    vector<int> edges, history, body;
    vector<Tile> tiles;
    vector<Part> parts;
    vector<std::array<int,4>> graph;
    std::map<int,vector<int>> portals;
    std::map<int,int> enemy_length;
    vector<int> enemy_heads, ally_heads;
    void setup(int width,int height) {
        w=width;h=height;n=w*h;edges.assign(2*n,-2);tiles.resize(n);
        parts.resize(n);graph.resize(n);
    }
    int neighbor(int c,int d) const {
        int x=c%w,y=c/w;
        if(d==0)y=(y+h-1)%h;if(d==1)x=(x+1)%w;
        if(d==2)y=(y+1)%h;if(d==3)x=(x+w-1)%w;
        return y*w+x;
    }
    int key(int c,int d) const {
        return d==0?c:d==2?neighbor(c,2):d==3?n+c:n+neighbor(c,1);
    }
    void learn(int k,const std::string &token) {
        int value=token=="."?-1:token=="w"?-3:std::stoi(token);
        if(edges[k]==value)return;
        int old=edges[k];
        if(old>=0) {
            auto &ends=portals[old];ends.erase(std::remove(ends.begin(),ends.end(),k),ends.end());
        }
        edges[k]=value;
        if(value>=0) {
            auto &ends=portals[value];
            if(std::find(ends.begin(),ends.end(),k)==ends.end())ends.push_back(k);
        }
    }
    void rebuild() {
        for(int c=0;c<n;c++)for(int d=0;d<4;d++) {
            int k=key(c,d),t=edges[k],v=-1;
            if(t==-1)v=neighbor(c,d);
            if(t==-2)v=-2;
            if(t>=0) {
                const auto &ends=portals[t];
                if(ends.size()==2) {
                    int other=ends[0]==k?ends[1]:ends[0];
                    v=(d==1||d==2)?other%n:neighbor(other%n,d);
                }
            }
            graph[c][d]=v;
        }
    }
    int next(int c,int d,bool future=false) const {
        int v=graph[c][d];return v==-2&&future?neighbor(c,d):v;
    }
    bool contains(const vector<int>&b,int c) const {
        return std::find(b.begin(),b.end(),c)!=b.end();
    }
    void reconstruct(const std::map<int,int> &mine) {
        if(history.empty()||history[0]!=head) {
            history={head};
            while((int)history.size()<length) {
                int found=-1;
                for(auto [c,d]:mine)if(!contains(history,c)&&next(c,d)==history.back()){found=c;break;}
                if(found<0)break;
                history.push_back(found);
            }
        }
        body.assign(history.begin(),history.begin()+std::min(length,(int)history.size()));
    }
    bool blocked(int c,const vector<int>&b) const {
        if(contains(b,c))return true;
        if(parts[c].id<0)return false;
        return parts[c].id!=id || !contains(body,c); // incomplete own-body reconstruction
    }
    bool confirmed(int c) const {return tiles[c].seen==round&&tiles[c].pearl==round;}
    bool food(int c,int eta,int window=0) const {
        const auto&t=tiles[c];
        return round-t.pearl<=P::memory_ttl ||
            (t.bed&&t.due>=round-3&&t.due<=round+eta-1+window);
    }
    vector<int> distances(int source,int max_depth=100000) const {
        vector<int> ds(n,-1),q={source};ds[source]=0;
        for(size_t i=0;i<q.size();i++) {
            int c=q[i];if(ds[c]>=max_depth)continue;
            for(int v:graph[c])if(v>=0&&ds[v]<0&&
                    (parts[v].id<0||parts[v].id==id)) {ds[v]=ds[c]+1;q.push_back(v);}
        }
        return ds;
    }
};
