「Kling AI」Service Level Agreement (SLA)

This Service Level Agreement (SLA) defines the service availability metrics and compensation scheme for the API solution provided by Kling AI.
Article 1 Definitions

1.1 Service Period: A service period is one calendar month. It refers to each calendar month included in the service term purchased by the customer. For example, if the customer purchases the service for three months starting from March 17, the service periods will include four months: the first service period is from March 17 to March 31, the second service period is from April 1 to April 30, the third service period is from May 1 to May 31, and the fourth service period is from June 1 to June 16. Service availability is calculated separately for each service period.

1.2 Error Request: Requests with an HTTP status code of 5XX and requests that do not reach Kling AI’s server due to Kling AI server faults are considered error requests, excluding the following types of requests:

(i) Error requests or service unavailability caused by reasonable upgrades, changes, or maintenance initiated by Kling AI;

(ii) Requests restricted by Kling AI’s service due to the customer’s application being hacked;

(iii) Errors resulting from domain bans due to content violations or other reasons.

1.3 Valid Request: Requests received by Kling AI’s server are considered valid requests.

1.4 Error Rate per 5 Minutes: Error rate per 5 minutes = (Number of error requests in 5 minutes / Number of valid requests in 5 minutes) x 100%

1.5 Monthly Service Fee: The fee incurred for Kling AI’s API solution services for a particular account within a service period.
Article 2 Service Availability

2.1 Service Availability Calculation Formula

Service availability is calculated based on the service period. The average error rate per 5 minutes is derived by dividing the sum of the error rates per 5 minutes by the total number of 5-minute intervals in the service period. Service availability is then calculated as:

Service Availability = (1 - ∑ Error Rate per 5 Minutes in Service Period / Total Number of 5-Minute Intervals in Service Period) x 100%

Note: Total number of 5-minute intervals in a service period = 12 x 24 x Number of Days in the Service Period.

2.2 Service Availability Commitment

Kling AI’s API solution service availability is committed to being no less than 99.90%. If this service availability commitment is not met, the customer can claim compensation as stipulated in Section 3 of this agreement. Compensation does not cover request failures or service unavailability caused by the following:

(i) System maintenance notified in advance by the service provider, including cutting, repair, upgrades, and fault simulations;

(ii) Network, equipment failures, or configuration adjustments outside the service provider’s equipment;

(iii) Hacking of the customer’s application or data;

(iv) Loss or leakage of data, credentials, or passwords due to improper maintenance or confidentiality by the customer;

(v) Service unavailability due to the customer not following product documentation or usage recommendations;

(vi) Issues caused by the customer’s own operating system upgrades;

(vii) Issues caused by the customer’s application or installation activities;

(viii) Issues caused by customer negligence or authorized user operations;

(ix) Force majeure and unforeseen events;

(x) Other unavailability caused by factors not attributable to the service provider.
Article 3 Compensation Scheme

3.1 Compensation Standard

Based on the monthly service availability of Kling AI’s API solution for a particular account, compensation amounts are calculated according to the following table. Compensation is provided in the form of vouchers for the Kling AI API solution and is capped at 50% of the monthly service fee for that account (excluding fees paid with vouchers).
Service Availability	Compensation Voucher Amount
Below 99.90% but at least 99.00%	10% of Monthly Service Fee
Below 99.00% but at least 95.00%	25% of Monthly Service Fee
Below 95.00%	50% of Monthly Service Fee

3.2 Compensation Application Deadline

Customers can apply for compensation for the previous month’s service unavailability after the fifth (5th) working day of each month. Compensation applications must be submitted within two (2) months after the end of the month in which the Kling AI API solution did not meet availability standards. Applications submitted beyond this deadline will not be accepted.
Article 4 Others

The service provider reserves the right to modify the terms of this SLA. Any modifications will be communicated to the customer by email at least 30 days in advance. If the customer does not agree with the modifications to the SLA, they have the right to stop using the Kling AI API solution. Continued use of the Kling AI API service will be considered as acceptance of the modified SLA.