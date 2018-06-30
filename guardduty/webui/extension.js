console.log('Loading guarduty Miner WebUI');

(function() {

function GuarddutySideConfigController($scope, MinemeldConfigService, MineMeldRunningConfigStatusService,
                                  toastr, $modal, ConfirmService, $timeout) {
    var vm = this;

    // side config settings
    vm.aws_access_key_id = undefined;
    vm.aws_secret_access_key = undefined;
    vm.region_name = undefined;
    vm.detector_id = undefined;

    vm.loadSideConfig = function() {
        var nodename = $scope.$parent.vm.nodename;

        MinemeldConfigService.getDataFile(nodename + '_side_config')
        .then((result) => {
            if (!result) {
                return;
            }

            if (result.aws_access_key_id) {
                vm.aws_access_key_id = result.aws_access_key_id;
            } else {
                vm.aws_access_key_id = undefined;
            }

            if (result.aws_secret_access_key) {
                vm.aws_secret_access_key = result.aws_secret_access_key;
            } else {
                vm.aws_secret_access_key = undefined;
            }

            if (result.region_name) {
                vm.region_name = result.region_name;
            } else {
                vm.region_name = undefined;
            }

            if (result.detector_id) {
                vm.detector_id = result.detector_id;
            } else {
                vm.detector_id = undefined;
            }
        }, (error) => {
            toastr.error('ERROR RETRIEVING NODE SIDE CONFIG: ' + error.status);
            vm.aws_access_key_id = undefined;
            vm.aws_secret_access_key = undefined;
            vm.region_name = undefined;
            vm.detector_id = undefined;
        });
    };

    vm.saveSideConfig = function() {
        var side_config = {};
        var hup_node = undefined;
        var nodename = $scope.$parent.vm.nodename;

        if (vm.aws_access_key_id) {
            side_config.aws_access_key_id = vm.aws_access_key_id;
        }
        if (vm.aws_secret_access_key) {
            side_config.aws_secret_access_key = vm.aws_secret_access_key;
        }
        if (vm.region_name) {
            side_config.region_name = vm.region_name;
        }
        if (vm.detector_id) {
            side_config.detector_id = vm.detector_id;
        }

        return MinemeldConfigService.saveDataFile(
            nodename + '_side_config',
            side_config
        );
    };

    vm.setAWSAccessKeyID = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/guarddutyWebui/guardduty.miner.sakid.modal.html',
            controller: ['$modalInstance', GuarddutyAccessKeyIDController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.aws_access_key_id = result.aws_access_key_id;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('AWS ACCESS KEY ID SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING AWS ACCESS KEY ID: ' + error.statusText);
        });
    };
    vm.setAWSSecretAccessKey = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/guarddutyWebui/guardduty.miner.ssak.modal.html',
            controller: ['$modalInstance', GuarddutySecretAccessKeyController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.aws_secret_access_key = result.aws_secret_access_key;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('AWS SECRET ACCESS KEY SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING AWS SECRET ACCESS KEY: ' + error.statusText);
        });
    };
    vm.setAWSRegion = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/guarddutyWebui/guardduty.miner.sar.modal.html',
            controller: ['$modalInstance', GuarddutyRegionController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.region_name = result.region_name;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('AWS REGION NAME SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING AWS REGION NAME: ' + error.statusText);
        });
    };
    vm.setDetectorID = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/guarddutyWebui/guardduty.miner.sdid.modal.html',
            controller: ['$modalInstance', GuarddutyDetectorIDController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.detector_id = result.detector_id;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('AWS DETECTOR ID SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING DETECTOR ID: ' + error.statusText);
        });
    };

    vm.loadSideConfig();
}

function GuarddutySecretAccessKeyController($modalInstance) {
    var vm = this;

    vm.aws_secret_access_key = undefined;
    vm.aws_secret_access_key2 = undefined;

    vm.valid = function() {
        if (vm.aws_secret_access_key2 !== vm.aws_secret_access_key) {
            angular.element('#fgPassword1').addClass('has-error');
            angular.element('#fgPassword2').addClass('has-error');

            return false;
        }
        angular.element('#fgPassword1').removeClass('has-error');
        angular.element('#fgPassword2').removeClass('has-error');

        if (!vm.aws_secret_access_key) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.aws_secret_access_key = vm.aws_secret_access_key;

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

function GuarddutyAccessKeyIDController($modalInstance) {
    var vm = this;

    vm.aws_access_key_id = undefined;

    vm.valid = function() {
        if (!vm.aws_access_key_id) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.aws_access_key_id = vm.aws_access_key_id;

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

function GuarddutyDetectorIDController($modalInstance) {
    var vm = this;

    vm.detector_id = undefined;

    vm.valid = function() {
        if (!vm.detector_id) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.detector_id = vm.detector_id;

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

function GuarddutyRegionController($modalInstance) {
    var vm = this;

    vm.region_name = undefined;

    vm.valid = function() {
        if (!vm.region_name) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.region_name = vm.region_name;

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

angular.module('guarddutyWebui', [])
    .controller('GuarddutySideConfigController', [
        '$scope', 'MinemeldConfigService', 'MineMeldRunningConfigStatusService',
        'toastr', '$modal', 'ConfirmService', '$timeout',
        GuarddutySideConfigController
    ])
    .config(['$stateProvider', function($stateProvider) {
        $stateProvider.state('nodedetail.guarddutyminerinfo', {
            templateUrl: '/extensions/webui/guarddutyWebui/guardduty.miner.info.html',
            controller: 'NodeDetailInfoController',
            controllerAs: 'vm'
        });
    }])
    .run(['NodeDetailResolver', '$state', function(NodeDetailResolver, $state) {
        NodeDetailResolver.registerClass('guardduty.node.Miner', {
            tabs: [{
                icon: 'fa fa-circle-o',
                tooltip: 'INFO',
                state: 'nodedetail.guarddutyminerinfo',
                active: false
            },
            {
                icon: 'fa fa-area-chart',
                tooltip: 'STATS',
                state: 'nodedetail.stats',
                active: false
            },
            {
                icon: 'fa fa-asterisk',
                tooltip: 'GRAPH',
                state: 'nodedetail.graph',
                active: false
            }]
        });

        // if a nodedetail is already shown, reload the current state to apply changes
        // we should definitely find a better way to handle this...
        if ($state.$current.toString().startsWith('nodedetail.')) {
            $state.reload();
        }
    }]);
})();