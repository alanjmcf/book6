## Deployment in the enterprise

Measuring the adoption of IPv6 in the enterprise domain is not straightforward.
Since it is hard to look at it from the network "inside", one of the few currently available approaches 
is to check the IPv6 readiness from outside the enterprise's network.
[NIST](https://fedv6-deployment.antd.nist.gov/cgi-bin/generate-com) provides a method to infer whether 
US enterprises support IPv6 by checking its external services, such as the availability of 
Domain Name System (DNS) AAAA records, of an IPv6-based mail service and of the support of IPv6 on
their website. The same method can be applied to [Chinese](http://218.2.231.237:5001/cgi-bin/generate) and
[Indian](https://cnlabs.in/IPv6_Mon/generate_industry.html) enterprises.

DNS has a good support in all cases: more than 50% of the enterprises in the three economies considered have AAAA records,
a sign that IPv6 support is generally available. The same cannot be said or the other services that have much lower adoption. The future RFC 
[IPv6 Status](https://datatracker.ietf.org/doc/draft-ietf-v6ops-ipv6-deployment/) provides other statistics about more specific industry domains.

What are the factors hindering the adoption of IPv6 in the enterprise?
Appendix B of [IPv6 Status](https://datatracker.ietf.org/doc/draft-ietf-v6ops-ipv6-deployment/) reports the result of 
a poll issued by the [Industry Network Technology Council (INTC)](https://industrynetcouncil.org/) to check the need for IPv6 training 
by some medium and large US enterprises.
   
The poll shows that lack of IPv6 knowledge is one of the main issues.
This reflects into the need for training, in particular in the areas of IPv6 security and
IPv6 troubleshooting. Apart from training, enterprises feel that IPv6 security is of operational concern as well as the 
conversion of the applications they use in their daily activity to IPv6.


* Addressing in the enterprise vertical

How organizations craft their addressing schemes will be varied and will likely be determined by a number of factors. The largest factor 
that will influence the procurement or otherwise obtaining of address resources will be organizational size. The size of a given organization 
often (but not always) dictates the criticality of networking resources which includes both physical assets (routers, switches, security appliances) 
as well as human resources, and the level of skill available either by direct employment or by contacted assistance. Also included in these resources 
is the logical elements requires for a presence on the global internet in the manner of addressing. Larger or more mature organizations may already 
posses network resources such as Autonomous System Numbers (ASNs), legacy IP resources, and possibly existing provider independent (PI) IPv6 space. 
First, it is important to make the distinction of address space types. There are really three different types of address allocations possible, provider 
independent, provider allocated, and unique local addressing. 

*Define each address type*

Organizations will need to understand the differences as it will be both dictated by resource availability and will inform routing policy and future deployment changes. 

**Provider Independent address space**
Provider Independent address space consists of address resources obtained directly from a regional internet registry (RIR). These address resources are allocated to a requesting entity 
after a formal request process that entails a light justification process and an annual fee collection. The addressing is allocated to the requesting entity and, within the scope of the global
internet best practices, can be used however the assigned entity sees fit. 


For PI address space based deployments, organizations will need to contract external consultancy or have in-house expertise in obtaining address space from a regional 
internet registry (RIR) that will be determined by the locality of their organization. Further, obtaining PI address space from an RIR means coordinating with their ISP(s) 
to route the PI space based on some routing policy with upstream provider(s). If an organization is not staffed to or does not have the experience or knowledge on the processes 
of obtaining address space and routing it globally (i.e. within the internet default free zone (DFZ)), it will be required to contract such tasks. In house or contracted IT 
support should understand the intricacies of routing policy of said PI address space in the appropriate routing registries, maintaining best practice filtering (MANRS), populating 
and maintaining internet route registry (IRR) data, implementing Resource Public Key Infrastructure (RPKI), and have at least a rudimentary understanding of what operating in the DFZ 
means. In general, maintaining PI address space offers the most flexibility and stability due to the portable nature of the resources, and although it does have a higher startup cost 
both operationally and financially, is the preferable method for medium to large enterprises.  


**Provider Assigned address space**
Provider Assigned (PA) address space consists of PI address space that is assigned to an upstream provider and sub-delegated to a customer or. 

If receiving PA from an upstream provider designs such as multihoming is a more involved process that will involve coordination with the upstream transit provider that owns the IP resources. 
*add more details here*
Additionally, renumbering is functionally required if said provider is exchanged for another unless NAT is employed as a translation tool obtaining additional address space may require more effort or may not be possible.

<!-- Link lines generated automatically; do not delete -->
### [<ins>Previous</ins>](Deployment%20in%20the%20home.md) [<ins>Chapter Contents</ins>](5.%20Deployment.md)
