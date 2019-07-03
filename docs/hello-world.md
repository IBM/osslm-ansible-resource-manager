# hello-world
A sample ansible resource is available to test the system.
To run the test:  

1. open the swagger ui
2. Expand *lifecycle-controller / Perform a transition against a Resource*
3. Enter this payload

```json
{"context": {},
"deploymentLocation": "world",
"metricKey": "a0644bba-1da3-4074-b84b-0f260f82e482",
"properties": {"prop1":"nouse"},
"resourceManagerId": "ansible",
"resourceName": "test",
"resourceType": "resource::hello-world::1.0",
"transitionName": "Install"}
```

4. Click *Try it out!*
5. :tada: You should get an "IN_PROGRESS" response
5. From the response copy the *requestId*
6. Expand *lifecycle-controller / get details on transition request status*
7. Paste the *requestId* and click *Try it out!*
8. :tada: You should get a "COMPLETED" response
9. From the response copy the *resourceId*
10. Expand *topology-controller / get details for a resource instance*
11. Paste the *resourceId* and click *Try it out!*
12. :tada: You should get the current time of the docker container in the response payload
